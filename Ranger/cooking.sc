Program Cooking;
  const
  RawFishSteaks = $097A;
  FishSteaks = $097B;
  
  var
  SteaksAmount : integer;
  SkillCooking : Double;

{$Include 'all.inc'}

procedure CheckCooking;
begin
SkillCooking := GetSkillValue('Cooking');
If SkillCooking < 33.0 Then 
  begin
  AddToSystemJournal ('Скилл Cooking: 33.0');
  AddToSystemJournal ('Купите его у рыбка рядом с банком в Британии.');
  While 1 = 1 Do Wait (100);
  end;
If (SkillCooking >= 33.0) and (SkillCooking < 50.0) and (SteaksAmount <> 1) Then
  begin
  AddToSystemJournal ('Скилл Cooking: 33.0 - 50.0');
  AddToSystemJournal ('Жарим по 1 стейку.');
  SteaksAmount := 1;
  end;  
If (SkillCooking >= 50.0) and (SkillCooking < 75.0) and (SteaksAmount <> 3) Then
  begin
  AddToSystemJournal ('Скилл Cooking: 50.0 - 75.0');
  AddToSystemJournal ('Жарим по 3 стейка.');
  SteaksAmount := 3;
  end;
If (SkillCooking >= 75.0) and (SkillCooking < 90.0) and (SteaksAmount <> 4) Then
  begin
  AddToSystemJournal ('Скилл Cooking: 75.0 - 90.0');
  AddToSystemJournal ('Жарим по 4 стейка.');
  SteaksAmount := 4;
  end;
If (SkillCooking >= 90.0) and (SkillCooking < 110.0) and (SteaksAmount <> 6) Then
  begin
  AddToSystemJournal ('Скилл Cooking: 90.0 - 110.0');
  AddToSystemJournal ('Жарим по 6 стейков.');
  SteaksAmount := 6;
  end;
If (SkillCooking >= 120.0) and (SkillCooking < 125.0) and (SteaksAmount <> 9) Then
  begin
  AddToSystemJournal ('Скилл Cooking: 120.0 - 125.0');
  AddToSystemJournal ('Жарим по 9 стейков.');
  SteaksAmount := 9;
  end;
If (SkillCooking >= 125.0) and (SkillCooking < 135.0) and (SteaksAmount <> 12) Then
  begin
  AddToSystemJournal ('Скилл Cooking: 125.0 - 135.0');
  AddToSystemJournal ('Жарим по 12 стейков.');
  SteaksAmount := 12;
  end;
If (SkillCooking >= 135.0) and (SkillCooking < 150.0) and (SteaksAmount <> 15) Then
  begin
  AddToSystemJournal ('Скилл Cooking: меньше 135.0 - 150.0');
  AddToSystemJournal ('Жарим по 15 стейков.');
  SteaksAmount := 15;
  end;
If (SkillCooking = 150.0) Then
  begin
  AddToSystemJournal ('Ваш скилл Cooking: 150.0');
  AddToSystemJournal ('Поздравляю!');
  While 1 = 1 Do Wait (100);
  end;
end;
  
procedure CheckRawFishSteaks;
begin
If GetQuantity(FindType(RawFishSteaks,BackPack)) < SteaksAmount Then
  begin
  If FindType(RawFishSteaks,Ground) > 0 Then 
    begin
    Grab (FindItem, 300);
    checklag (30000);
    wait (500)
    FindType(RawFishSteaks,Ground);
    AddToSystemJournal('Осталось сырых стейков: '+IntToStr(FindFullQuantity));
    end;
  end;  
end;

procedure DropFishSteaks;
begin
  While FindType(FishSteaks,backpack) > 0 Do
    begin
    Stack(FishSteaks,$0000);
    checklag (30000);
    wait (500)
    FindType(FishSteaks,Ground);
    AddToSystemJournal('Уже нажарили стейков: '+IntToStr(FindFullQuantity));
    end;
end;

procedure MakeSteaks;
begin
While GetQuantity(FindType(RawFishSteaks,BackPack)) >= SteaksAmount Do
  begin
  CloseMenu;
  CancelMenu;
  if MenuHookPresent = True then CancelMenu;
  if SteaksAmount = 1 then
    WaitMenu('What do','cooked fishsteak')
  else
    WaitMenu('What do','cooked fishsteak ('+IntToStr(SteaksAmount)+')');
  hungry(1,-1);
  Useobject(findtype(RawFishSteaks,backpack));
  WaitJournalLine(Now,'Darn|You put|You must', 10000);
  wait (1000)
  end;
end;

Begin
SetARStatus (True);
SetPauseScriptOnDisconnectStatus(True);
SteaksAmount := 0;
While Dead = False Do 
  begin
  CheckCooking;
  DropFishSteaks;
  CheckRawFishSteaks;
  MakeSteaks;
  end
end.
