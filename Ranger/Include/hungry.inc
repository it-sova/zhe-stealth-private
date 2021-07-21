procedure Hungry(NeededLevel : Integer; Container : Cardinal);
var
    FoodID : Cardinal;
begin
if Not Connected then Exit;

FindType($097B,-1);
if (FindCount > 0) and (Luck < 90) then
   FoodID := FindType($097B, -1);
   if FoodID <> $00 then UseObject(FoodID);
   CheckLag(30000);
   wait(1000);
End;