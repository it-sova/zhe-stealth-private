program kinding_autotile;
var
TyleType : Array [0..34] of Word;
a : TFoundTilesArray;
c,b,s,i : Integer;

const
Xmin = 1853;
Ymin = 1204;

Xmax = 1847;
Ymax = 1158;

AxeType = $0F51;    // чем режим ветки (стоит дагер)


{$Include 'all.inc'}


procedure DropKindle;
begin
CheckLag (30000);
wait(500);
FindType($0DE1,Backpack);
AddToSystemJournal('Kindles Count : ' + IntToStr(FindCount));
if FindCount > 0 then Drophere(finditem);  
end;

procedure BurnKindle;
begin
CheckLag (30000);
wait(1000);
FindType($0DE1,Ground);
while (FindCount > 0) and (not Dead) do 
begin
  FindType($0DE1,Ground);
  if FindCount > 0 then     
    begin 
     useobject(finditem); 
     wait(3500); 
     WaitJournalLine(Now, 'Looping', 20000);
    end;
end;
end;



procedure CheckEquip;
 Var EquipAxe : Cardinal;
 begin
 if (GetType(ObjAtLayer(RhandLayer)) <> AxeType) then
  begin
   Disarm;
   CheckLag (30000);
   wait(500);
   FindType(AxeType, Backpack);
   if (FindCount > 0) then
    begin
     EquipAxe := finditem;
     Equip(RhandLayer, EquipAxe);
     CheckLag (30000);
     wait(500);
    end
   end;
 end;



Begin
SetARStatus(True);
Addtosystemjournal('Скрипт успешно стартовал.');
TyleType[0] := 3230;
TyleType[1] := 3272;
TyleType[2] := 3274;
TyleType[3] := 3275;
TyleType[4] := 3276;
TyleType[5] := 3277;
TyleType[6] := 3278;
TyleType[7] := 3280;
TyleType[8] := 3281;
TyleType[9] := 3283;
TyleType[10] := 3284;
TyleType[11] := 3286;
TyleType[12] := 3287;
TyleType[13] := 3288;
TyleType[14] := 3289;
TyleType[15] := 3290;
TyleType[16] := 3291;
TyleType[17] := 3292;
TyleType[18] := 3293;
TyleType[19] := 3294;
TyleType[20] := 3295;
TyleType[21] := 3296;
TyleType[22] := 3299;
TyleType[23] := 3300;
TyleType[24] := 3302;
TyleType[25] := 3303;
TyleType[26] := 3384;
TyleType[27] := 3385;
TyleType[28] := 3391;
TyleType[29] := 3392;
TyleType[30] := 3394;
TyleType[31] := 3395;
TyleType[32] := 3417;
TyleType[33] := 3440;
TyleType[34] := 3460;
while true do
 begin
 while (not dead) and (connected) do
  begin
   WaitConnection(3000);
   for s := 0 to 34 do
      begin
      b:= GetStaticTilesArray(Xmin,Ymin,Xmax,Ymax, 0, TyleType[s], a); 
      AddToSystemJournal('Tile Count : ' + IntToStr(b));
      for c :=0 to b-1 do    
         begin
         CheckLag (30000);
         CheckEquip;
         NewMoveXY(a[c].X,a[c].Y, False, 1, True);
         CheckLag (30000);
         wait(500);
         Hungry(1,-1);
         If TargetPresent Then CancelTarget;
         if (GetType(ObjAtLayer(RhandLayer)) = AxeType) then  
         begin
         for i:= 0 to 20 do  // ставим сколько раз тыкаем по дереву (стоит 20 раз)
           begin
            CheckLag (30000);        
            Hungry(1,-1);
            WaitTargetTile((TyleType[s]),(a[c].X),(a[c].Y),(a[c].Z)); 
            UseObject(ObjAtLayer(RhandLayer));
            CheckLag (30000);
            WaitJournalLine(Now, 'cannot see|far away|finished looping|Looping aborted|fail|chip off|not', 20000);
           end;   
           CheckLag (30000);
           DropKindle;
           wait(1000);
           BurnKindle;
           wait(500);
           end;
         end;
      end;
  end;
 if (dead) or (not connected) then wait(1000);
 end;
end.
