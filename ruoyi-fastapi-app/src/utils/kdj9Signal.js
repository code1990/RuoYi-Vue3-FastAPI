export const kdj9Signal = {
  ID: "KDJ9_SIGNAL",
  Name: "KDJ9 信号",
  Description: "9 周期 KDJ 与 NM 共振信号",
  IsMainIndex: false,
  Script: `RSV:=(C-LLV(L,9))/(HHV(H,9)-LLV(L,9))*100;
K:SMA(RSV,3,1);
D:SMA(K,3,1);
J:(3*K-2*D)/100;
NM:4*SMA((C-LLV(L,5))/(HHV(H,5)-LLV(L,5))*100,5,1)-3*SMA(SMA((C-LLV(L,5))/(HHV(H,5)-LLV(L,5))*100,5,1),3,1);
DRAWICON(CROSS(RSV,K),10,1);
DRAWICON(CROSS(RSV,D),30,1);
DRAWICON(CROSS(D,RSV),30,2);
DRAWICON(CROSS(K,RSV),10,2);`,
};

export const registerKdj9Signal = indexScript => indexScript.AddIndex([kdj9Signal]);
