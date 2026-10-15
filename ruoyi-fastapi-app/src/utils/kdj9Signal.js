export const kdj9Signal = {
  ID: "KDJ9_SIGNAL",
  Name: "KDJ9 信号",
  Description: "9 周期 KDJ 与 NM 共振信号",
  IsMainIndex: false,
  Script: `X_1:=9;
X_2:=3;
X_3:=3;
X_4:=0.5;
上位线:=0.8;
下位线:=0.2;
顶位线:=1;
底位线:=0;
X_5:(CLOSE-LLV(LOW,X_1))/(HHV(HIGH,X_1)-LLV(LOW,X_1))*100;
X_6:SMA(X_5,X_2,1);
X_7:SMA(X_6,X_3,1);
J:(3*X_6-2*X_7)/100;
JJ:SMA(J,2,1);
JJJ:=X_5-X_6;
K1:CROSS(X_5,X_6);
K2:CROSS(X_5,X_7);
DRAWICON(K1,10,1);
DRAWICON(K2,30,1);
DRAWICON(CROSS(X_7,X_5),30,2);
DRAWICON(CROSS(X_6,X_5),10,2);
K11:J<0.1 AND J>REF(J,1);
DRAWICON(K11,60,1);
均线1:=EMA(C,2);
均线2:=EMA(SLOPE(C,9)*20+C,37);
K3:CROSS(均线1,均线2);
NM:4*SMA((C-LLV(L,5))/(HHV(H,5)-LLV(L,5))*100,5,1)-3*SMA(SMA((C-LLV(L,5))/(HHV(H,5)-LLV(L,5))*100,5,1),3.2,1);
K4:CROSS(NM,7);
K5:CROSS(NM,3);
DD:K4*100;
DD3:K5*30;
K6:K1+K2+K3+K4+K5;`,
};

export const registerKdj9Signal = indexScript => indexScript.AddIndex([kdj9Signal]);
