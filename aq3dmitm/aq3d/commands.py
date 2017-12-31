from enum import Enum

class Type(Enum) :
    NULL = 0
    Move = 1
    NpcMove = 2
    Login = 3
    Chat = 4
    Joinmychannels = 5
    Channel = 6
    Area = 7
    Cell = 8
    Command = 9
    Item = 10
    Trade = 11
    Combat = 12
    NPCTemplates = 13
    SpellTemplates = 14
    Quest = 15
    Loot = 16
    Entity = 17
    NPC = 18
    Machine = 19
    PvPFlag= 20
    Emote = 21
    _DEBUG = 22
    Report = 23
    _Unused = 24
    Message = 25
    CombatClasses = 26
    Misc = 27
    Merge = 28
    Friend = 29
    Disconnect = 30
    StartSummon = 31
    Party = 32
    Bank = 33
    EndTransfer = 34

class CmdBank(Enum) :
    NULL = 0
    LoadItems = 1
    TransferItem = 2
    PurchaseSlot = 3


class CmdMove(Enum) :
    NULL = 0
    Full = 1
    Synch = 2
    Keys = 3
    Jump = 4

class CmdNpcMove(Enum) :
    NULL = 0
    Path = 1
    Speed = 2
    Stop = 3

class CmdLogin(Enum) :
    Token = 0x01
    Login = 0xFF

class CmdChat(Enum) :
    NULL = 0
    Multi = 1
    Whisper = 2
    Party = 3

class CmdArea(Enum) :
    NULL = 0
    Join = 1
    Remove = 2
    List = 3
    WarSync = 4

class CmdCell(Enum) :
    NULL = 0
    Join = 1
    Add = 2
    Remove = 3
    Teleport = 4

class CmdChannel(Enum) :
    NULL = 0
    Join = 1
    Add = 2
    Remove = 3

class CmdCommand(Enum) :
    NULL = 0
    Admin = 1
    Join = 2

class CmdItem(Enum) :
    NULL = 0
    Equip = 1
    Unequip = 2
    UpdateQty = 3
    Destroy = 4
    Add = 5
    Use_Unused = 6
    Fuse = 7
    Claim = 8
    DailyReward = 9

class CmdTrade(Enum) :
    NULL = 0
    Buy = 1
    Sell = 2
    ShopLoad = 3

class CmdCombat(Enum) :
    NULL = 0
    SpellRequest = 1
    SpellTrigger = 2
    SpellCancel = 3
    Spell = 4
    EffectPulse = 5
    Item = 6
    IAO = 7
    MachineSpell = 8
    EffectRemove = 9
    ResetCD = 10

class CmdQuest(Enum) :
    NULL = 0
    Load = 1
    Accept = 2
    Abandon = 3
    Complete = 4
    Progress = 5

class CmdLoot(Enum) :
    NULL = 0
    AddDropBag = 1
    RemoveDropItem = 2
    GetDropItem = 3
    RollStart = 4
    RollItem = 5
    PassItem = 6

class CmdEntity(Enum) :
    NULL = 0
    AddGoldXP = 1
    LevelUp = 2
    Update = 3
    PlayerRespawn = 4
    Stats = 5
    Class = 6
    MCUpdate = 7
    GoldUpdate = 8
    BitFlagUpdate = 9
    AssetOverride = 10
    Customize = 11
    EnergyUpdate = 12
    DataSync = 13
    KillSelf = 14
    TransferMap = 15
    AssetUpdate = 16

class CmdNPC(Enum) :
    NULL = 0
    Despawn = 1
    Spawn = 2
    Talk = 3

class CmdMachine(Enum) :
    NULL = 0
    TransferPad = 1
    Update = 2
    Click = 3
    Enter = 4
    Exit = 5

class CmdPvPFlag(Enum) :
    NULL = 0

class CmdEmote(Enum) :
    NULL = 0

class CmdDebug(Enum) :
    NULL = 0

class CmdReport(Enum) :
    NULL = 0

class CmdUnused(Enum) :
    NULL = 0

class CmdMessage(Enum) :
    NULL = 0

class CmdClass(Enum) :
    NULL = 0
    Add = 1
    Equip = 2
    Train = 3
    Reset = 4
    List = 5

class CmdMisc(Enum) :
    NULL = 0
    Notify = 1

class CmdMerge(Enum) :
    NULL = 0
    Merge = 1
    MergeShopLoad = 2
    Claim = 3
    BuyOut = 4
    Speedup = 5
    Add = 6
    Remove = 7

class CmdFriend(Enum) :
    NULL = 0
    Summon = 1
    StartSummon = 2
    Request = 3
    Add = 4
    Delete = 5
    List = 6
    Goto = 7
    GotoAsk = 8
    SyncIgnore = 9
    Added = 10

class ItemTransferResponseType(Enum) :
    Success = 0
    EquippedItem = 1
    Duplicate = 2
    NotFound = 3
    Failure = 4
    QuestItem = 5 

class BankSlotPurchaseResponse(Enum) :
    Success = 0
    NSF = 1
    Failure = 2

class CmdBank(Enum) :
    NULL = 0
    BankItems = 1
    ItemTransfer = 2
    BankPurchase = 3

class CmdParty(Enum) :
    NULL = 0
    Invite = 1
    Join = 2
    Remove = 3
    Promote = 4
    List = 5
    AreaCreate = 6
    AreaGoto = 7
    Goto = 8

class CmdEndTransfer(Enum) :
    End = 0xFF

def subtype(x) :
    "maps to a sub type"
    if x == Type.Move :
        return CmdMove
    elif x == Type.NpcMove :
        return CmdNpcMove
    elif x == Type.Login :
        return CmdLogin
    elif x == Type.Chat :
        return CmdChat
    elif x == Type.Joinmychannels :
        return CmdJoinmychannels
    elif x == Type.Channel :
        return CmdChannel
    elif x == Type.Area :
        return CmdArea
    elif x == Type.Cell :
        return CmdCell
    elif x == Type.Command :
        return CmdCommand
    elif x == Type.Item :
        return CmdItem
    elif x == Type.Trade :
        return CmdTrade
    elif x == Type.Combat :
        return CmdCombat
    elif x == Type.NPCTemplates :
        return CmdNPCTemplates
    elif x == Type.SpellTemplates :
        return CmdSpellTemplates
    elif x == Type.Quest :
        return CmdQuest
    elif x == Type.Loot :
        return CmdLoot
    elif x == Type.Entity :
        return CmdEntity
    elif x == Type.NPC :
        return CmdNPC
    elif x == Type.Machine :
        return CmdMachine
    elif x == Type.PvPFlag :
        return CmdPvPFlag
    elif x == Type.Emote :
        return CmdEmote
    elif x == Type._DEBUG :
        return CmdDebug
    elif x == Type.Report :
        return CmdReport
    elif x == Type._Unused :
        return CmdUnused
    elif x == Type.Message :
        return CmdMessage
    elif x == Type.CombatClasses :
        return CmdClass
    elif x == Type.Misc :
        return CmdMisc
    elif x == Type.Merge :
        return CmdMerge
    elif x == Type.Friend :
        return CmdFriend
    # Disconnect = 30 # client has no parsing for this, only calls disconnect
    # StartSummon = 31 # not processed by client, maybe server?
    elif x == Type.Party :
        return CmdParty
    elif x == Type.Bank :
        return CmdBank
    elif x == Type.EndTransfer :
        return CmdEndTransfer
    else :
        raise ValueError("Not supported class")
        # return lambda x: x

                        
