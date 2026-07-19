local clamp = math.Clamp
local max = math.max
local sin = math.sin
local CurTime = CurTime
local FrameTime = FrameTime
local Lerp = Lerp

local narcoticVignette = Material("effects/shaders/zb_vignette")
local sedationLerp = 0
local respiratoryLerp = 0

local colour = {
    ["$pp_colour_addr"] = 0,
    ["$pp_colour_addg"] = 0,
    ["$pp_colour_addb"] = 0,
    ["$pp_colour_brightness"] = 0,
    ["$pp_colour_contrast"] = 1,
    ["$pp_colour_colour"] = 1,
    ["$pp_colour_mulr"] = 0,
    ["$pp_colour_mulg"] = 0,
    ["$pp_colour_mulb"] = 0
}

local function GetViewedPlayer()
    local localPlayer = IsValid(lply) and lply or LocalPlayer()
    if not IsValid(localPlayer) then return nil end

    if localPlayer:Alive() then return localPlayer end

    local spectated = localPlayer:GetNWEntity("spect")
    if IsValid(spectated) then return spectated end

    return nil
end

hook.Add("Post Post Processing", "ZCity Narcotic Effects", function()
    local ply = GetViewedPlayer()
    local targetSedation = IsValid(ply) and ply:GetNWFloat("zcity_narcotic_sedation", 0) or 0
    local targetRespiratory = IsValid(ply) and ply:GetNWFloat("zcity_narcotic_respiratory", 0) or 0
    local antagonist = IsValid(ply) and ply:GetNWFloat("zcity_narcotic_antagonist", 0) or 0

    if IsValid(ply) and istable(ply.organism) then
        local analgesia = max(tonumber(ply.organism.analgesia) or 0, 0)
        targetSedation = max(targetSedation, analgesia * 0.35)
        targetRespiratory = max(targetRespiratory, max(analgesia - 1, 0) * 0.8)
    end

    local blend = clamp(FrameTime() * 3, 0, 1)
    sedationLerp = Lerp(blend, sedationLerp, targetSedation)
    respiratoryLerp = Lerp(blend, respiratoryLerp, targetRespiratory)

    local sedation = clamp((sedationLerp - 0.12) / 1.68, 0, 1)
    local overdose = clamp((respiratoryLerp - 0.45) / 2.15, 0, 1)
    local reversal = clamp(antagonist, 0, 1)

    if sedation <= 0.001 and overdose <= 0.001 and reversal <= 0.001 then return end

    local pulse = (sin(CurTime() * (0.75 + overdose * 0.35)) + 1) * 0.5
    local tunnel = clamp(overdose * (0.75 + pulse * 0.25), 0, 1)

    colour["$pp_colour_addr"] = 0.012 * sedation - 0.018 * overdose
    colour["$pp_colour_addg"] = 0.004 * sedation - 0.022 * overdose
    colour["$pp_colour_addb"] = -0.006 * sedation - 0.028 * overdose
    colour["$pp_colour_brightness"] = 0.008 * sedation - 0.075 * tunnel + 0.015 * reversal
    colour["$pp_colour_contrast"] = 1 - 0.08 * sedation - 0.24 * tunnel + 0.06 * reversal
    colour["$pp_colour_colour"] = 1 - 0.16 * sedation - 0.58 * tunnel + 0.12 * reversal
    colour["$pp_colour_mulr"] = 0.015 * sedation
    colour["$pp_colour_mulg"] = 0.004 * sedation
    colour["$pp_colour_mulb"] = 0

    DrawColorModify(colour)

    if sedation > 0.02 or overdose > 0.02 then
        DrawMotionBlur(
            0.025 + overdose * 0.07,
            clamp(0.08 + sedation * 0.22 + overdose * 0.58, 0, 0.9),
            0.01
        )
    end

    if tunnel > 0.01 then
        render.UpdateScreenEffectTexture()
        narcoticVignette:SetFloat("$c2_x", CurTime() + 20000)
        narcoticVignette:SetFloat("$c0_z", tunnel * 1.7)
        narcoticVignette:SetFloat("$c1_y", tunnel * 3.2)
        render.SetMaterial(narcoticVignette)
        render.DrawScreenQuad()
    end
end)

hook.Add("Player_Death", "ZCity Reset Narcotic Effects", function(ply)
    local localPlayer = IsValid(lply) and lply or LocalPlayer()
    if ply ~= localPlayer then return end
    sedationLerp = 0
    respiratoryLerp = 0
end)
