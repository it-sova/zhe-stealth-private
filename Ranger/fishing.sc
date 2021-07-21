Program Fising;
type
WaterRecord = Record
t,x,y,z,a: integer;
end;

var
WaterTile: array[0..50] of integer;
WaterPlace: array[0..500] of WaterRecord;
WaterCount: integer;
x,y,c,a,i: integer;
s: boolean;

{$Include 'all.inc'}


const
{Настройка контейнеров: Указать ID контейнеров}
WoodChest = $4C18B024; //Сундук с удачками.
mainbag   = $4C18B024; //Сумка в которую будет соберать гп и ракушки.
Trash     = $4C0A95DE; //Мусорка, будет выкидывать морскую траву и пустые сумки.
Map       = $4C0A95DE; //Сундук с картами.если не нужны, ставим айди треша.
SOS       = $4C0A95DE; //Сундук с сос картами.если не нужны, ставим айди треша.
net       = $4C0A95DE; //Сундук с сетями. если сети не нужны, ставим айди треша.
trap      = $4C010610; //трап лодки
{Конец настройки контейнеров}
{Ракушки}
SeaDollar     = $0FC8;
CapShells     = $0FC5;
AquaShells    = $0FC4;
SeaNymphs     = $0FC6;
Neptune       = $0FC7;
MermaidShells = $0FCA;
DiviniaShells = $0FC9;
{/Ракушки. Если Есть еще ракушки, будут добовалятся}

fishpole      = $0DC0;  //тайп удочек
fishpolecolor = $0000;  //цвет удочек
dagger        = $0F51;
steak         = $097A;

procedure CheckGold;
var bag : Cardinal;
begin
  FindDistance := 2;
  repeat
    Ignore(mainbag);
    findtype($0e75, ground);
    if (FindCount >= 1) and (GetDistance(finditem) <=2) and (GetDistance(finditem) >=0) and connected and (not dead) then begin //
      bag := finditem;
      useobject(bag);
      CheckLag (30000);
      wait(500);
      if (FindCount < 1) then begin
        MoveItem(bag, 0, Trash, 0, 0, 0);
        CheckLag (30000);
        wait(500);
      end;
      findtypeEx($0EED,$0000,bag,True);
      if (FindCount > 0) then begin
        MoveItem(findtype($0EED,bag), 0, mainbag, 0, 0, 0);
        CheckLag (30000);
        wait(500);
      end;
      begin
        FindTypeEx(bag,$0000,ground,false);
        MoveItem(bag, 0, Trash, 0, 0, 0);
        CheckLag (30000);
        wait(500);
      end;
    end;
  until (FindCount < 1) or dead;
end;

procedure Seashell;
begin
  FindDistance := 2;
  repeat
    FindType(SeaDollar, backpack);
    if (FindCount >= 1) and (GetDistance(finditem) <=2) and (GetDistance(finditem) >=0) and connected and (not dead) then begin
      MoveItem(finditem, 0, mainbag, 0, 0, 0);
      CheckLag (30000);
      wait(500);
    end;
      FindType(CapShells, backpack);
      if (FindCount >= 1) and (GetDistance(finditem) <=2) and (GetDistance(finditem) >=0) and connected and (not dead) then begin
        MoveItem(finditem, 0, mainbag, 0, 0, 0);
        CheckLag (30000);
        wait(500);
      end;
      FindType(AquaShells, backpack);
      if (FindCount >= 1) and (GetDistance(finditem) <=2) and (GetDistance(finditem) >=0) and connected and (not dead) then begin
        MoveItem(finditem, 0, mainbag, 0, 0, 0);
        CheckLag (30000);
        wait(500);
      end;
      FindType(SeaNymphs, backpack);
      if (FindCount >= 1) and (GetDistance(finditem) <=2) and (GetDistance(finditem) >=0) and connected and (not dead) then begin
        MoveItem(finditem, 0, mainbag, 0, 0, 0);
        CheckLag (30000);
        wait(500);
      end;
      FindType(Neptune, backpack);
      if (FindCount >= 1) and (GetDistance(finditem) <=2) and (GetDistance(finditem) >=0) and connected and (not dead) then begin
        MoveItem(finditem, 0, mainbag, 0, 0, 0);
        CheckLag (30000);
        wait(500);
      end;
      FindType(MermaidShells, backpack);
      if (FindCount >= 1) and (GetDistance(finditem) <=2) and (GetDistance(finditem) >=0) and connected and (not dead) then begin
        MoveItem(finditem, 0, mainbag, 0, 0, 0);
        CheckLag (30000);
        wait(500);
      end;
      FindType(DiviniaShells, backpack);
      if (FindCount >= 1) and (GetDistance(finditem) <=2) and (GetDistance(finditem) >=0) and connected and (not dead) then begin
        MoveItem(finditem, 0, mainbag, 0, 0, 0);
        CheckLag (30000);
        wait(500);
      end;
      FindType($1F03, backpack);
      if (FindCount >= 1) and (GetDistance(finditem) <=2) and (GetDistance(finditem) >=0) and connected and (not dead) then begin
        MoveItem(finditem, 0, Trash, 0, 0, 0);
        CheckLag (30000);
        wait(500);
      end;
      FindType($1F03, ground);
      if (FindCount >= 1) and (GetDistance(finditem) <=2) and (GetDistance(finditem) >=0) and connected and (not dead) then begin
        MoveItem(finditem, 0, Trash, 0, 0, 0);
        CheckLag (30000);
        wait(500);
      end;
    until (FindCount < 1) or dead;
end;

procedure MoveSos;
begin
  FindDistance := 2;
  repeat
    FindType($099F, backpack);
    if (FindCount >= 1) and (GetDistance(finditem) <=2) and (GetDistance(finditem) >=0) and connected and (not dead) then begin
      MoveItem(finditem, 0, SOS, 0, 0, 0);
      CheckLag (30000);
      wait(500);
    end;
  until (FindCount < 1) or dead;
end;

procedure MoveMap;
begin
  FindDistance := 2;
  repeat
    FindType($14ED,ground);
    if (FindCount >= 1) and (GetDistance(finditem) <=2) and (GetDistance(finditem) >=0) and connected and (not dead) then begin
      MoveItem(finditem, 0, Map, 0, 0, 0);
      CheckLag (30000);
      wait(500);
    end;
  until (FindCount < 1) or dead;
end;

procedure seaweed;
begin
  FindDistance := 2;
  repeat
    FindType($0DBA, ground);
    if (FindCount >= 1) and (GetDistance(finditem) <=2) and (GetDistance(finditem) >=0) and connected and (not dead) then begin
      MoveItem(finditem, 0, mainbag, 0, 0, 0);
      CheckLag (30000);
      wait(500);
    end;
  until (FindCount < 1) or dead;
end;

procedure netl;
begin
  FindDistance := 2;
  repeat
    FindType($0DCA, backpack);
    if (FindCount >= 1) and (GetDistance(finditem) <=2) and (GetDistance(finditem) >=0) and connected and (not dead) then begin
      FindTypeEx($0DCA,$012C,backpack,True);
      MoveItem(finditem, 0, net, 0, 0, 0);
      CheckLag (30000);
      wait(500);
    end;
  until (FindCount < 1) or dead;
end;

procedure Rawsteak;
  begin
    FindDistance := 2;
    FindTypeEx(steak,$0000,backpack,true);
    if FindQuantity > 100 then
        begin
          Stack(steak,$0000);
          CheckLag (30000);
          wait(500);
          FindType(steak,Ground);
          Addtosystemjournal(IntToStr(FindFullQuantity) + ' стейков.');
        end;
  end;

procedure CheckRawsteak;
 begin
   FindType(steak, Backpack);
   if (Count(steak) > 0) then
   begin
      Rawsteak;
   end;
end;

procedure CheckDagger;
begin
  if (RHandLayer<>dagger) then begin
    Equipt(RHandLayer, dagger);
  end;
end;



procedure CheckWaterTile;
var
t: integer;
LCount: integer;
TTile: TStaticCell;
begin
  TTile:=ReadStaticsXY(x, y, WorldNum);
  LCount:=GetLayerCount(x, y, WorldNum);
  i:=0;
  while i < LCount do
  begin
    for t:=0 to 6 do
    begin
      if TTile.Statics[0].Tile=WaterTile[t] then
      begin
        WaterPlace[c].t:=TTile.Statics[0].Tile;
        WaterPlace[c].x:=x;
        WaterPlace[c].y:=y;
        WaterPlace[c].z:=TTile.Statics[0].z;
        WaterPlace[c].a:=1;
        c:=c+1;
      end;
    end;
    i:=i+1;
  end;
end;

procedure FindWaterTile;
begin
  for x:=GetX(self)-7 to GetX(self)+7 do
  for y:=GetY(self)-7 to GetY(self)+7 do
  begin
    CheckWaterTile;
  end;
  WaterCount:=c-1;
end;

procedure CheckEquip;
begin
  FindDistance := 2;
  if (not dead) and (connected) then
  begin
   FindTypeEx(fishpole,fishpolecolor,WoodChest,True);
   if FindQuantity = 0 then
    begin
     useobject(WoodChest);
     checklag(30000);
     wait(500);
  end;
    if (getquantity(findtype(fishpole,WoodChest)) > 0) and (gettype(ObjAtLayer(LhandLayer)) <> gettype(finditem)) then
    begin
      addtosystemjournal('Удочек осталось: '+inttostr(findcount-1)+'.');
       UnEquip(LHandLayer);
       checklag(30000);
       wait(500);
       FindTypeEx(fishpole,fishpolecolor,WoodChest,True);
       Equip(LhandLayer, finditem);
       checklag(30000);
       wait(500);
     end;
 end;
 end;


procedure CheckLaq; //если из-за лага удочка упадет в пак, она вернется в сундук.
  begin
   FindTypeEx(fishpole,fishpolecolor,backpack,True);
   if FindQuantity > 0 then
       begin
         MoveItem(finditem, 0, WoodChest, 0, 0, 0);
         checklag(30000);
         wait(500);
       end;
  end;

procedure OnRejectMoveItem(Reason: Byte);
begin
  AddToSystemJournal('Event! Muver');
end;

procedure Fishing;
begin
  useobject(WoodChest);
  checklag(30000);
  wait(500);
  for a:=0 to WaterCount do
  begin
    hungry (1,-1);
    checklag(30000);
    if WaterPlace[a].a = 1 then begin
      WaitTargetTile(WaterPlace[a].t, WaterPlace[a].x, WaterPlace[a].y, WaterPlace[a].z);
      wait(1000);
      if Length(LastJournalMessage)=34 then begin
        WaterPlace[a].a:=0;
        AddToSystemJournal('Заброкован таил');
      end;
      if (GetType(ObjAtLayer(LhandLayer)) < 1) then begin
      CheckEquip;
      wait(500);
      end;
      hungry (1,-1);
      UseObject(ObjAtLayer(LhandLayer));
      WaitJournalLine(Now,'You finished|see that|seem to get any fish here|You stop fishing|',100000);
      SetEventProc(evRejectMoveItem,'OnRejectMoveItem');
      CheckGold;
      Seashell;
      MoveSos;
      MoveMap;
      seaweed;
      netl;
      CheckLaq;
      wait(500);
      CheckRawsteak;
    end;
  end;
end;

procedure OnSpeech(Text, SenderName : String; SenderId : Cardinal);
  var
      DangerousMessages: array[0..3] of string;
      Danger: boolean;
      Counter: integer;
  begin
      DangerousMessages[0] := 'elemental';
      DangerousMessages[1] := 'alligator';
      DangerousMessages[2] := 'serpent';
      DangerousMessages[3] := 'attacking';
      Danger := false;
      for Counter := 0 to 3 do
      begin
          if BMSearch(1, Text, DangerousMessages[Counter]) > 0 then
          begin
              Danger := true;
              AddToSystemJournal('Dangerous message: '+DangerousMessages[Counter]);
          end;
      end;
      if Danger then
      begin
          AddToSystemJournal('Guarded');
          UOSay('.guards');
      end;
  end;

begin
  SetEventProc(evSpeech, 'OnSpeech');
  SetARStatus(true);
  UOSay('.autoloop 10');
  useobject(WoodChest);
  checklag(30000);
  wait(500);
  useobject(trap);
  checklag(30000);
  wait(500);
  s:=true;
  WaterTile[0]:=6038;
  WaterTile[1]:=6039;
  WaterTile[2]:=6040;
  WaterTile[3]:=6041;
  WaterTile[4]:=6042;
  WaterTile[5]:=6043;
  WaterTile[6]:=6044;
  FindWaterTile;
  AddToSystemJournal('Найдено тайлов для рыбалки: '+IntToStr(WaterCount));
while s do
 begin
  while not Dead and connected do
   begin
    CheckDagger;
    CheckEquip;
    Fishing;
   end;
  while Dead and connected do
   begin
    wait(1000);
   end;
  while not connected do
   begin
    wait(1000);
   end;
 end;
end.
