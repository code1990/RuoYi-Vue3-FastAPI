const createKdjSignal = period => ({
  ID: `KDJ${period}_SIGNAL`,
  Name: `KDJ${period} 信号`,
  Description: `${period} 周期 KDJ 与 NM 共振信号`,
  IsMainIndex: false,
  Script: `RSV:=(C-LLV(L,${period}))/(HHV(H,${period})-LLV(L,${period}))*100;
K:SMA(RSV,3,1);
D:SMA(K,3,1);
J:(3*K-2*D)/100;
NM:4*SMA((C-LLV(L,5))/(HHV(H,5)-LLV(L,5))*100,5,1)-3*SMA(SMA((C-LLV(L,5))/(HHV(H,5)-LLV(L,5))*100,5,1),3,1);
DRAWICON(CROSS(RSV,K),10,1);
DRAWICON(CROSS(RSV,D),30,1);
DRAWICON(CROSS(D,RSV),30,2);
DRAWICON(CROSS(K,RSV),10,2);`,
});

export const kdj9Signal = createKdjSignal(9);
export const kdj90Signal = createKdjSignal(90);
export const registerKdjSignals = indexScript => indexScript.AddIndex([kdj9Signal, kdj90Signal]);
