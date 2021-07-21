program taming;
var

Char : Array[1..2] of string;
Zver : Array[1..4] of Cardinal;

procedure Hungry();
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
if FindType($097B,-1) = 0 then AddToSystemJournal('No Food');
End;

procedure IsCurMessages;
var D : TDateTime;
begin
{5 minutes in DateTime = 5 / 1440 = 0.00347}
D := Now - (0.00697);
InJournalBetweenTimes(CharName + ': I am already performing another action.',D,Now);

if LineCount > 1 then
begin
AddToSystemJournal('Error with target. Disconnected');
Disconnect;
end;
end;


procedure First();

var
b : TDateTime;
tmp,i : integer;
lol : String;

Begin
lol:=Char[2]+': all release';

while True do
begin
IsCurMessages;

i:=0;
while i < 5 do
begin
for tmp:=1 to 4 do
begin
Hungry();
wait(500);
WaitTargetObject(zver[tmp]);
UseSkill('Animal Taming');
B:=Now+0.0001157407407;
WaitJournalLine(Now, 'You successfully tame|You failed', 30000);
{WaitJournalLine(Now, lol, 15000);}
UOsay('all release');
UOsay(IntToStr(tmp));
i := i + 1;
end;
end;
End;
End;

procedure Second();
var

i,tmp : integer;
f : TDateTime;

begin
f:=Now;
while true do
begin

IsCurMessages;


i:=0;
while i < 5 do
begin
Hungry();
WaitJournalLine(f,Char[1]+': 1'+'|'+Char[1]+': 2'+'|'+Char[1]+': 3'+'|'+Char[1]+': 4',0);
if InJournalBetweenTimes(Char[1]+': 1',f,Now) >= 0 then tmp := 1;
if InJournalBetweenTimes(Char[1]+': 2',f,Now) >= 0 then tmp := 2;
if InJournalBetweenTimes(Char[1]+': 3',f,Now) >= 0 then tmp := 3;
if InJournalBetweenTimes(Char[1]+': 4',f,Now) >= 0 then tmp := 4;

f:=Now;
WaitTargetObject(Zver[tmp]);
UseSkill('Animal Taming');

WaitJournalLine(Now,'You successfully tame|You fail', 45000);

UOsay('all release');
i := i + 1;
end;
End;
End;

begin
SetARStatus(true);
   Char[1]:='Belinda'; {Ник первого игрока }
   Char[2]:='Grandin'; {Ник второго игрока }
   Zver[1]:=$0027EFB9; {Айди животных }
   Zver[2]:=$00284D26; {Айди животных }
   Zver[3]:=$00284D27; {Айди животных }
   Zver[4]:=$00284D29; {Айди животных }
Case CharName Of
Char[1] : First();
Char[2] : Second();
else AddToSystemJournal('Error');
End;
End.
