if not SERVER then return end

hg = hg or {}
hg.organism = hg.organism or {}

local Narcotics = hg.organism.narcotics or {}
hg.organism.narcotics = Narcotics

Narcotics.Version = 1
Narcotics.Profiles = {
    morphine = {
        Label = "Morphine",
        HalfLife = 300,
        Sedation = 0.45,
        Respiratory = 0.35,
        Nausea = 0.10
    },
    fentanyl = {
        Label = "Fentanyl",
        HalfLife = 180,
        Sedation = 1.80,
        Respiratory = 2.60,
        Nausea = 0.45
    },
    painkillers = {
        Label = "Painkillers",
        HalfLife = 360,
        Sedation = 0.12,
        Respiratory = 0.04,
        Nausea = 0.05
    }
}

local max = math.max
local min = math.min
local clamp = math.Clamp
local approach = math.Approach
local exp = math.exp
local log = math.log
local isfunction = isfunction
local IsValid = IsValid
local CurTime = CurTime

local function EnsureState(org)
    org.narcoticLevels = org.narcoticLevels or {}
    org.narcoticBurden = org.narcoticBurden or 0
    org.narcoticSedation = org.narcoticSedation or 0
    org.narcoticRespiratoryDepression = org.narcoticRespiratoryDepression or 0
    org.narcoticAntagonist = org.narcoticAntagonist or 0
    org.narcoticLastDose = org.narcoticLastDose or 0
    return org.narcoticLevels
end

function Narcotics.AddDose(org, profileName, amount, source)
    if not istable(org) then return false end

    local profile = Narcotics.Profiles[profileName]
    amount = tonumber(amount) or 0
    if not profile or amount <= 0 then return false end

    local levels = EnsureState(org)
    levels[profileName] = clamp((levels[profileName] or 0) + amount, 0, 8)
    org.narcoticLastDose = CurTime()
    org.narcoticLastSource = IsValid(source) and source or nil
    org.narcoticLastProfile = profileName

    return true
end

function Narcotics.ApplyNaloxone(org, amount)
    if not istable(org) then return false end

    amount = clamp(tonumber(amount) or 1, 0, 1)
    EnsureState(org)
    org.narcoticAntagonist = max(org.narcoticAntagonist or 0, amount)
    return true
end

hg.organism.AddNarcoticDose = Narcotics.AddDose
hg.organism.ApplyNarcoticAntagonist = Narcotics.ApplyNaloxone

hook.Add("Org Clear", "ZCity Narcotics", function(org)
    org.narcoticLevels = {}
    org.narcoticBurden = 0
    org.narcoticSedation = 0
    org.narcoticRespiratoryDepression = 0
    org.narcoticAntagonist = 0
    org.narcoticLastDose = 0
    org.narcoticLastSource = nil
    org.narcoticLastProfile = nil
    org.narcoticNextNetwork = nil

    if IsValid(org.owner) and org.owner:IsPlayer() then
        org.owner:SetNWFloat("zcity_narcotic_burden", 0)
        org.owner:SetNWFloat("zcity_narcotic_sedation", 0)
        org.owner:SetNWFloat("zcity_narcotic_respiratory", 0)
        org.owner:SetNWFloat("zcity_narcotic_antagonist", 0)
    end
end)

local LN2 = log(2)

hook.Add("Org Think", "ZCity Narcotics", function(owner, org, timeValue)
    if not istable(org) then return end

    local dt = clamp(tonumber(timeValue) or 0, 0, 0.25)
    if dt <= 0 then return end

    local levels = EnsureState(org)
    local antagonist = max(clamp((org.naloxone or 0) / 4, 0, 1), clamp(org.narcoticAntagonist or 0, 0, 1))
    local activeMultiplier = 1 - antagonist * 0.97
    local clearanceMultiplier = 1 + antagonist * 48

    local burden = 0
    local sedation = 0
    local respiratory = 0
    local nausea = 0

    for profileName, level in pairs(levels) do
        local profile = Narcotics.Profiles[profileName]
        if not profile then
            levels[profileName] = nil
        else
            level = max(tonumber(level) or 0, 0)
            if level > 0 then
                local decay = exp(-(LN2 / max(profile.HalfLife or 240, 1)) * dt * clearanceMultiplier)
                level = level * decay
                if level < 0.0001 then level = 0 end
                levels[profileName] = level

                local active = level * activeMultiplier
                burden = burden + active
                sedation = sedation + active * (profile.Sedation or 0)
                respiratory = respiratory + active * (profile.Respiratory or 0)
                nausea = nausea + active * (profile.Nausea or 0)
            end
        end
    end

    org.narcoticAntagonist = approach(org.narcoticAntagonist or 0, 0, dt / 120)
    org.narcoticBurden = clamp(burden, 0, 8)
    org.narcoticSedation = clamp(sedation, 0, 6)
    org.narcoticRespiratoryDepression = clamp(respiratory, 0, 6)

    local sedationStress = max(org.narcoticSedation - 0.20, 0)
    local respiratoryStress = max(org.narcoticRespiratoryDepression - 0.45, 0)

    if sedationStress > 0 and isnumber(org.consciousness) then
        local target = clamp(1 - sedationStress * 0.38, 0.05, 1)
        if org.consciousness > target then
            org.consciousness = approach(org.consciousness, target, dt * (0.025 + sedationStress * 0.09))
        end
    end

    if respiratoryStress > 0 and istable(org.o2) and isnumber(org.o2[1]) then
        org.o2[1] = max(org.o2[1] - dt * respiratoryStress * 8, 0)
    end

    if sedationStress > 0 then
        org.disorientation = max(org.disorientation or 0, clamp(sedationStress * 0.8 + respiratoryStress * 0.45, 0, 5))
    end

    if nausea > 0.20 and isnumber(org.wantToVomit) then
        org.wantToVomit = min(org.wantToVomit + dt * (nausea - 0.20) * 0.05, 1.25)
    end

    if org.narcoticSedation > 1.25 or org.narcoticRespiratoryDepression > 1.75 then
        org.needfake = true
    end

    if org.narcoticRespiratoryDepression > 2.40 and istable(org.o2) and (org.o2[1] or 30) < 12 then
        org.needotrub = true
    end

    if IsValid(owner) and owner:IsPlayer() then
        org.narcoticNextNetwork = org.narcoticNextNetwork or 0
        if org.narcoticNextNetwork <= CurTime() then
            owner:SetNWFloat("zcity_narcotic_burden", org.narcoticBurden)
            owner:SetNWFloat("zcity_narcotic_sedation", org.narcoticSedation)
            owner:SetNWFloat("zcity_narcotic_respiratory", org.narcoticRespiratoryDepression)
            owner:SetNWFloat("zcity_narcotic_antagonist", antagonist)
            org.narcoticNextNetwork = CurTime() + 0.25
        end
    end
end)

local function WrapMedicine(className, profileName, doseScale, fallbackDose, antagonist)
    local stored = weapons.GetStored(className)
    if not stored or stored.ZCityNarcoticWrapped then return false end
    if not isfunction(stored.Heal) then return false end

    local original = stored.Heal
    stored.Heal = function(self, ent, mode)
        local before = self.modeValues and tonumber(self.modeValues[1]) or 0
        local administeringOwner = IsValid(self:GetOwner()) and self:GetOwner() or nil
        local doseRecorded = self.ZCityNarcoticDoseRecorded == true

        if IsValid(ent) and istable(ent.organism) and not antagonist then
            if IsValid(administeringOwner) and istable(administeringOwner.injectedinto) and IsValid(ent.organism.owner) then
                administeringOwner.injectedinto[ent.organism.owner] = 0
            end
        end

        local result = original(self, ent, mode)
        local after = IsValid(self) and self.modeValues and tonumber(self.modeValues[1]) or before

        if IsValid(ent) and istable(ent.organism) then
            local delivered = max(before - after, 0) * (doseScale or 1)
            local consumed = result == true or not IsValid(self)

            if delivered <= 0 and consumed and fallbackDose and not doseRecorded then
                delivered = fallbackDose
                if IsValid(self) then self.ZCityNarcoticDoseRecorded = true end
            end

            if delivered > 0 then
                if antagonist then
                    Narcotics.ApplyNaloxone(ent.organism, delivered)
                else
                    Narcotics.AddDose(ent.organism, profileName, delivered, administeringOwner)
                end
            end
        end

        return result
    end

    stored.ZCityNarcoticWrapped = true
    return true
end

local function PatchMedicines()
    local patched = 0
    patched = patched + (WrapMedicine("weapon_morphine", "morphine", 1) and 1 or 0)
    patched = patched + (WrapMedicine("weapon_fentanyl", "fentanyl", 1) and 1 or 0)
    patched = patched + (WrapMedicine("weapon_painkillers", "painkillers", 0.4, 0.4) and 1 or 0)
    patched = patched + (WrapMedicine("weapon_painkillers_tpik", "painkillers", 0.3, 0.3) and 1 or 0)
    patched = patched + (WrapMedicine("weapon_naloxone", nil, 1, 1, true) and 1 or 0)
    return patched
end

hook.Add("InitPostEntity", "ZCity Narcotic Weapon Profiles", PatchMedicines)
hook.Add("OnReloaded", "ZCity Narcotic Weapon Profiles", function()
    timer.Simple(0, PatchMedicines)
end)

timer.Simple(0, PatchMedicines)

concommand.Add("zcity_narcotics_status", function(ply)
    if IsValid(ply) and not ply:IsAdmin() then return end

    local target = IsValid(ply) and ply or nil
    local org = IsValid(target) and target.organism or nil
    if not org then
        if IsValid(ply) then ply:ChatPrint("No organism state available.") end
        return
    end

    local message = string.format(
        "narcotics burden=%.2f sedation=%.2f respiratory=%.2f antagonist=%.2f",
        org.narcoticBurden or 0,
        org.narcoticSedation or 0,
        org.narcoticRespiratoryDepression or 0,
        max(clamp((org.naloxone or 0) / 4, 0, 1), org.narcoticAntagonist or 0)
    )

    if IsValid(ply) then ply:ChatPrint(message) else print(message) end
end)
