
/////////////////////////////////////////////////////////////////////
//  模拟测试数据V2
//  
//
/////////////////////////////////////////////////////////////////////
import { JSNetwork } from "./umychart.network.wechart.js"

var TEST_URL="https://cdn.jsdelivr.net/npm/hqchart/src/jscommon/umychart.testdata/";

function HQData()  { }

HQData.Explain="本地测试数据";

HQData.NetworkFilter=function(data, callback)
{
    console.log(`[HQData::NetworkFilter] ${HQData.Explain}`, data);

    switch(data.Name) 
    {
        case 'MinuteChartContainer::RequestMinuteData':                 //分时图数据对接
            HQData.Minute_RequestMinuteData(data, callback);
            break;
        case "MinuteChartContainer::RequestHistoryMinuteData":          //多日分时图
            HQData.Minute_RequestHistoryMinuteData(data, callback);
            break;

        case "MinuteChartContainer::RequestOverlayMinuteData":
            HQData.Minute_RequestOverlayMinuteData(data, callback);
            break;

        case "MinuteChartContainer::RequestOverlayHistoryMinuteData":
            HQData.Minute_RequestOverlayHistoryMinuteData(data, callback);
            break;

        case 'KLineChartContainer::RequestHistoryData':                 //日线全量数据下载
            HQData.RequestHistoryData(data,callback);
            break;
        case 'KLineChartContainer::RequestRealtimeData':                //日线实时数据更新
            HQData.RequestRealtimeData(data,callback);
            break;
        case 'KLineChartContainer::RequestFlowCapitalData':             //流通股本
            HQData.RequestFlowCapitalData(data,callback);
            break;

        case "KLineChartContainer::RequestOverlayHistoryData":          //叠加股票
            //HQChart使用教程30-K线图如何对接第3方数据16-日K叠加股票
            HQData.RequestOverlayHistoryData(data, callback);
            break;

        case "KLineChartContainer::RequestOverlayHistoryMinuteData":
            //HQChart使用教程30-K线图如何对接第3方数据17- 分钟K叠加股票
            HQData.RequestOverlayHistoryMinuteData(data, callback);
            break;

        case 'KLineChartContainer::ReqeustHistoryMinuteData':           //分钟全量数据下载
            HQData.RequestHistoryMinuteData(data, callback);
            break;
        case 'KLineChartContainer::RequestMinuteRealtimeData':          //分钟增量数据更新
            HQData.RequestMinuteRealtimeData(data,callback);
            break;

        case "KLineChartContainer::RequestDragDayData":              //拖动下载
            HQData.RequestDragDayData(data, callback);
            break;

        case "KLineChartContainer::RequestDragMinuteData":           //分钟拖动下载
            HQData.RequestDragMinuteData(data, callback);
            break;

        case "JSSymbolData::GetVariantData":                            //额外的变量数据
            HQData.RequestIndexVariantData(data,callback);
            break;

        case "JSSymbolData::GetOtherSymbolData":
            HQData.RequestOtherSymbolData(data, callback);
            break;

        case "AnnouncementInfo::RequestData":
            HQData.AnnouncementInfo_RequestData(data,callback);
            break;

        case "PforecastInfo::RequestData":
            HQData.PforecastInfo_RequestData(data,callback);
            break;

        case "InvestorInfo::RequestData":
            HQData.InvestorInfo_RequestData(data,callback);
            break;

        case "ResearchInfo::RequestData":
            break;

        case "BlockTrading::RequestData":
            HQData.BlockTrading_RequestData(data,callback);
            break;

        case "TradeDetail::RequestData":
            HQData.TradeDetail_RequestData(data,callback);
            break;

        case "JSSymbolData::GetGPJYValue":
            HQData.GPJYValue_RequestData(data,callback);
            break;
        case "JSSymbolData::GetSCJYValue":
            HQData.SCJYValue_RequestData(data,callback);
            break;
        case "JSSymbolData::GetBKJYValue":
            HQData.BKJYValue_RequestData(data,callback);
            break;

        case "JSSymbolData::GetGPJYOne":
            HQData.GPJYOne_RequestData(data,callback);
            break;
        case "JSSymbolData::GetSCJYOne":
            HQData.SCJYOne_RequestData(data,callback);
            break;
        case "JSSymbolData::GetBKJYOne":
            HQData.BKJYOne_RequestData(data,callback);
            break;
        case "JSSymbolData::GetFinValue":
            HQData.FinValue_RequestData(data,callback);
            break;
        case "JSSymbolData::GetFinOne":
            HQData.FinOne_RequestData(data,callback);
            break;
    }
}

HQData.Minute_RequestMinuteData=function(data, callback)
{
    data.PreventDefault=true;
    var symbol=data.Request.Data.symbol[0]; //请求的股票代码
    var dayCount=data.Request.Data.daycount;
    console.log(`[HQData::Minute_RequestMinuteData] Symbol=${symbol}`);

    this.GetDayMinuteDataBySymbol(symbol, (fullData)=>
    {
        var stockItem=fullData[0];
        var hqchartData={ code:0, name:symbol, symbol: symbol, stock:[stockItem]};
    
        callback({data:hqchartData});
    });
    
}

HQData.Minute_RequestHistoryMinuteData=function(data, callback)
{
    data.PreventDefault=true;
    var symbol=data.Request.Data.symbol; //请求的股票代码
    var dayCount=data.Request.Data.daycount;
    console.log(`[HQData::Minute_RequestHistoryMinuteData] Symbol=${symbol}`);

    this.GetMulitDayMinuteDataBySymbol(symbol, (fullData)=>
    {
        var hqchartData={ code:0, data:[], name:symbol, symbol: symbol };

        var start=fullData.length-dayCount;
        if (start<0) start=0;
    
        hqchartData.data=fullData.slice(start);
        
        callback({data:hqchartData});
    });
  
}

HQData.Minute_RequestOverlayMinuteData=function (data, callback) 
{
    data.PreventDefault=true;
    var symbol=data.Request.Data.symbol;
    var date=data.Request.Data.days[0];

    HQData.GetMulitDayMinuteDataBySymbol(symbol,(fullData)=>
    {
        var aryDay=HQData.GetMulitDayMinuteDataByDate(fullData, [date]);

        var hqchartData={ code:0, data:aryDay, name:symbol, symbol:symbol  };
        callback({data:hqchartData});
    });
    
}

HQData.Minute_RequestOverlayHistoryMinuteData=function(data, callback)
{
    data.PreventDefault=true;
    var symbol=data.Request.Data.symbol;
    var aryDate=data.Request.Data.days;
    HQData.GetMulitDayMinuteDataBySymbol(symbol, (fullData)=>
    {
        var aryDay=HQData.GetMulitDayMinuteDataByDate(fullData, aryDate);
        var hqchartData={ code:0, data:aryDay, name:symbol, symbol:symbol  };
        callback({data:hqchartData});
    });
    
}

HQData.RequestHistoryData=function(data,callback)
{
    data.PreventDefault=true;
    var symbol=data.Request.Data.symbol; //请求的股票代码
    var count=data.Request.Data.count
    console.log(`[HQData::RequestMinuteDaysData] Symbol=${symbol}`);
    
   HQData.GetDayKLineDataBySymbol(symbol, (fullData)=>
    {
        var aryData=[];
        if (HQData.IsNonEmptyArray(fullData))
        {
            var dataCount=fullData.length;
            var start=dataCount-count;
            if (start<0) start=0;
            aryData=fullData.slice(start);
        }
        var hqchartData={ name:symbol, symbol:symbol, data:aryData, ver:2.0 };
    
        callback({data:hqchartData});
    });
}

HQData.RequestFlowCapitalData=function(data,callback)
{
    data.PreventDefault=true;
    var symbol=data.Request.Data.symbol; //请求的股票代码

    console.log(`[HQData::RequestFlowCapitalData] Symbol=${symbol}`);

    var hqchartData=KLINE_CAPITAL_DATA;
    callback({data:hqchartData});
}

HQData.RequestRealtimeData=function(data,callback)
{
    data.PreventDefault=true;
    var symbol=data.Request.Data.symbol[0]; //请求的股票代码
    var end=data.Request.Data.dateRange.End;
    var endDate=end.Date;
    var aryStock=[];

    for(var i=0;i<data.Request.Data.symbol.length;++i)
    {
        var item=data.Request.Data.symbol[i];
        HQData.GetDayKLineDataBySymbol(item, (fullData, symbol)=>
        {
            if (!HQData.IsNonEmptyArray(fullData)) return;

            var aryData=HQData.GetKLineDataByDate(fullData, endDate, 20999999);
            if (!HQData.IsNonEmptyArray(aryData)) return;
    
            var kItem=aryData[0];
            var price=kItem[5];
            var value=Math.ceil(Math.random()*10)/1000*price;
            var bUp=Math.ceil(Math.random()*10)>=5;
            if (bUp) price+=value;
            else price-=value;
    
            var stockItem={ symbol:symbol, name:symbol };
            stockItem.date=kItem[0];
            stockItem.yclose=kItem[1];
            stockItem.open=kItem[2];
            stockItem.high=Math.max(kItem[3],price);
            stockItem.low=Math.min(kItem[4],price);
            stockItem.price=price;
            stockItem.vol=kItem[6];
            stockItem.amount=kItem[7];
    
            aryStock.push(stockItem);

            if (aryStock.length==data.Request.Data.symbol.length)
            {
                var hqchartData={ code:0, stock:aryStock };
                callback({data:hqchartData});
            }
        });
        
    }
}


HQData.RequestHistoryMinuteData=function(data, callback)
{
    data.PreventDefault=true;
    var symbol=data.Request.Data.symbol; //请求的股票代码
    var count=data.Request.Data.count*200;  //请求的数据长度

    console.log(`[HQData::RequestHistoryMinuteData] Symbol=${symbol}`);

    HQData.GetM1KLineDataBySymbol(symbol, (fullData)=>
    {
        var aryData=[];
        if (HQData.IsNonEmptyArray(fullData))
        {
            var dataCount=fullData.length;
            var start=dataCount-count;
            if (start<0) start=0;
            aryData=fullData.slice(start);
        }
    
        var hqchartData={ name:symbol, symbol:symbol, data:aryData, ver:2.0 };
    
        callback({data:hqchartData});
    });
}


HQData.RequestMinuteRealtimeData=function(data,callback)
{
    data.PreventDefault=true;
    var symbol=data.Request.Data.symbol[0]; //请求的股票代码
    var end=data.Request.Data.dateRange.End;
    var endDate=end.Date;
    var endTime=end.Time;

    console.log(`[HQData::RequestMinuteRealtimeData] Symbol=${symbol}`);

    var aryOverlay=[ ];     //叠加
    var aryMainData=[];     //主图
    var recvCount=0;
    for(var i=0;i<data.Request.Data.symbol.length;++i)
    {
        var symbol=data.Request.Data.symbol[i];
        HQData.GetM1KLineDataBySymbol(symbol, (fullData, code)=>
        {
            ++recvCount;

            if (!HQData.IsNonEmptyArray(fullData)) return;

            var aryData=HQData.GetKLineDataByDateTime(fullData, endDate, endTime, 20999999, 9999);
            if (!HQData.IsNonEmptyArray(aryData)) return;
    
            var kItem=JSON.parse(JSON.stringify(aryData[0]));
    
            //生成随机测试数据
            var price=kItem[5];
            var value=Math.ceil(Math.random()*10)/10000*price;
            var bUp=Math.ceil(Math.random()*10)>=5;
            
            if (bUp) price+=value;
            else price-=value;
            kItem[5]=price;
            kItem[3]=Math.max(price, kItem[3]);
            kItem[4]=Math.min(price, kItem[4]);
    
            if (recvCount==1)
            {
                aryMainData.push(kItem);
            }
            else
            {
                var stock={ data:[kItem], symbol:code, name:code };
                aryOverlay.push(stock);
            }           

            if (recvCount==data.Request.Data.symbol.length)
            {
                var hqchartData={ name:symbol, symbol:symbol, ver:2.0, data:aryMainData };
                if (HQData.IsNonEmptyArray(aryOverlay)) hqchartData.overlay=aryOverlay;
                callback({data:hqchartData});
            }
        });
       
    }

   
   
   
}


HQData.RequestIndexVariantData=function(data,callback)
{
    var varName=data.Request.Data.VariantName;  //变量名称
    if (varName=="FROMOPEN") 
    {
        var hqchartData={  };
        //单数据
        hqchartData.Data={ Date:20230707, Value:240 };
        hqchartData.DataType=1;
        callback({data:hqchartData});
    }

}

HQData.RequestOtherSymbolData=function(data, callback)
{
    data.PreventDefault=true;
    var symbol=data.Request.Data.symbol;
    var period=data.Request.Data.period;
    var right=data.Request.Data.right;
    var hqchartData=null;
    if (ChartData.IsDayPeriod(period,true)) hqchartData=KLINE_DAY_DATA2;
    else if (ChartData.IsMinutePeriod(period,true)) hqchartData=KLINE_MINUTE_DATA2;
    hqchartData.name=symbol;
    hqchartData.symbol=symbol;
    callback({data:hqchartData});
}

HQData.AnnouncementInfo_RequestData=function(data,callback)
{
    data.PreventDefault=true;
    var symbol=data.Request.Symbol;

    var hqchartData={ symbol:symbol, report:[] };

    var kData=data.HQChart.ChartPaint[0].Data;
    for(var i=0, j=1;i<kData.Data.length;++i)
    {
        var kItem=kData.Data[i];
        if (i%10!=4) continue;

        var itemReport={ releasedate:kItem.Date, time:kItem.Time, title:`公告(${j}) xxxx`, }

        hqchartData.report.push(itemReport);

        ++j;
    }

    callback({data:hqchartData});
}


HQData.PforecastInfo_RequestData=function(data,callback)
{
    data.PreventDefault=true;
    var symbol=data.Request.Symbol;

    var hqchartData={ symbol:symbol, report:[] };

    var kData=data.HQChart.ChartPaint[0].Data;
    for(var i=0, j=1;i<kData.Data.length;++i)
    {
        var kItem=kData.Data[i];
        if (i%10!=4) continue;

        var itemReport={ date:kItem.Date, time:kItem.Time, title:`公告(${j}) xxxx`, }

        hqchartData.report.push(itemReport);

        ++j;
    }

    callback({data:hqchartData});
}

HQData.InvestorInfo_RequestData=function(data,callback)
{
    data.PreventDefault=true;
    var symbol=data.Request.Symbol;

    callback({data:TEST_NEWSINTERACT_DATA});
}

HQData.BlockTrading_RequestData=function(data,callback)
{
    data.PreventDefault=true;
    var symbol=data.Request.Symbol;

    callback({data:TEST_BLOCK_TRADING_DATA});
}

HQData.TradeDetail_RequestData=function(data,callback)
{
    data.PreventDefault=true;
    var symbol=data.Request.Symbol;

    callback({data:TEST_TRADE_DETAL_DATA});
}

//GPJYVALUE(ID,N,TYPE),ID为数据编号,N表示第几个数据(取1或2),TYPE:为1表示做平滑处理,没有数据的周期返回上一周期的值;为0表示不做平滑处理;2表示没有数据则为0.
HQData.GPJYValue_RequestData=function(data,callback)
{
    data.PreventDefault=true;
    var symbol=data.Request.Data.symbol;
    var id=data.Request.Data.Args[0];
    var n=data.Request.Data.Args[1];
    var type=data.Request.Data.Args[2];

    var aryData=[];
    var kData=data.Self.Data;
    for(var i=0;i<kData.Data.length;++i)
    {
        var kItem=kData.Data[i];
        if (i%50==15)
        {
            var value=HQData.GetRandomTestData(10,100)
            aryData.push({ Date:kItem.Date, Time:kItem.Time, Value:value });
        }
    }
    
    callback(aryData);
}

HQData.SCJYValue_RequestData=function(data,callback)
{
    data.PreventDefault=true;
    var symbol=data.Request.Data.symbol;
    var id=data.Request.Data.Args[0];
    var n=data.Request.Data.Args[1];
    var type=data.Request.Data.Args[2];

    var aryData=[];
    var kData=data.Self.Data;
    for(var i=0;i<kData.Data.length;++i)
    {
        var kItem=kData.Data[i];
        if (i%50==20)
        {
            var value=HQData.GetRandomTestData(1000,2000)
            aryData.push({ Date:kItem.Date, Time:kItem.Time, Value:value });
        }
    }
    
    callback(aryData);
}

HQData.BKJYValue_RequestData=function(data,callback)
{
    data.PreventDefault=true;
    var symbol=data.Request.Data.symbol;
    var id=data.Request.Data.Args[0];
    var n=data.Request.Data.Args[1];
    var type=data.Request.Data.Args[2];

    var aryData=[];
    var kData=data.Self.Data;
    for(var i=0;i<kData.Data.length;++i)
    {
        var kItem=kData.Data[i];
        if (i%60==33)
        {
            var value=HQData.GetRandomTestData(500,1000)
            aryData.push({ Date:kItem.Date, Time:kItem.Time, Value:value });
        }
    }
    
    callback(aryData);
}

HQData.GPJYOne_RequestData=function(data,callback)
{
    data.PreventDefault=true;
    var symbol=data.Request.Data.symbol;
    var id=data.Request.Data.Args[0];
    var n=data.Request.Data.Args[1];
    var year=data.Request.Data.Args[2];
    var day=data.Request.Data.Args[3];

    var value=HQData.GetRandomTestData(800,1200);
    callback({ Date:20230509, Value:value});
}

HQData.SCJYOne_RequestData=function(data,callback)
{
    data.PreventDefault=true;
    var symbol=data.Request.Data.symbol;
    var id=data.Request.Data.Args[0];
    var n=data.Request.Data.Args[1];
    var year=data.Request.Data.Args[2];
    var day=data.Request.Data.Args[3];

    var value=HQData.GetRandomTestData(400,500);
    callback({ Date:20230509, Value:value});
}

HQData.BKJYOne_RequestData=function(data,callback)
{
    data.PreventDefault=true;
    var symbol=data.Request.Data.symbol;
    var id=data.Request.Data.Args[0];
    var n=data.Request.Data.Args[1];
    var year=data.Request.Data.Args[2];
    var day=data.Request.Data.Args[3];

    var value=HQData.GetRandomTestData(900,2000);
    callback({ Date:20230509, Value:value});
}

HQData.FinValue_RequestData=function(data,callback)
{
    data.PreventDefault=true;
    var symbol=data.Request.Data.symbol;
    var id=data.Request.Data.Args[0];

    var aryData=[];
    var kData=data.Self.Data;
    for(var i=0;i<kData.Data.length;++i)
    {
        var kItem=kData.Data[i];
        if (i%60==21)
        {
            var value=HQData.GetRandomTestData(10,20)
            aryData.push({ Date:kItem.Date, Time:kItem.Time, Value:value });
        }
    }
    
    callback(aryData);
}

HQData.FinOne_RequestData=function(data,callback)
{
    data.PreventDefault=true;
    var symbol=data.Request.Data.symbol;
    var id=data.Request.Data.Args[0];
    var year=data.Request.Data.Args[1];
    var day=data.Request.Data.Args[2];

    var value=HQData.GetRandomTestData(80,90);
    callback({ Date:20230509, Value:value});
}

HQData.RequestOverlayHistoryData=function(data, callback)
{
    data.PreventDefault=true;
    var symbol=data.Request.Data.symbol;
    var first=data.Request.Data.first;
    var fullData=HQData.GetDayKLineDataBySymbol(symbol, (fullData)=>
    {
        var aryData=[];
        if (HQData.IsNonEmptyArray(fullData))
        {
            aryData=HQData.GetKLineDataByDate(fullData, first.date, 20999999)
        }
    
        var hqchartData={  code:0, symbol: symbol,name: symbol, ver:2.0, data:aryData };
    
        callback({data:hqchartData});
    });
    
}

HQData.RequestOverlayHistoryMinuteData=function(data, callback)
{
    data.PreventDefault=true;
    var symbol=data.Request.Data.symbol;
    var first=data.Request.Data.first;
    var aryData=[];
   
    HQData.GetM1KLineDataBySymbol(symbol, (fullData, symbol)=>
    {
        if (fullData)
        {
            aryData=HQData.GetKLineDataByDateTime(fullData, first.date, first.time, 20999999, 9999)
        }
    
        var hqchartData={  symbol: symbol,name: symbol, ver:2.0, data:aryData };
    
        callback({data:hqchartData});
    });
   
}

HQData.RequestDragDayData=function(data, callback)
{
    data.PreventDefault=true;
    var dataCount=data.Option.XShowCount;
    var symbol=data.Request.Data.symbol;        //请求的股票代码
    var firstDateTime=data.Request.Data.first;
    var aryOverlay=data.Request.Data.overlay;   //叠加股票

    console.log(`[HQData::RequestDragDayData] Symbol=${symbol} date=${firstDateTime.date} time=${firstDateTime.time}`);

    var self=data.Self;
    self.IsOnTouch = false;
    self.LastMovePoint=null;

    var option=data.Option;
    var title=`拖动下载数据中...... 起始位置 ${firstDateTime.date}, 下载数据个数${dataCount}`
    self.EnableSplashScreen({Title:title, Draw:true });

   
    var findIndex=-1;
    var date=firstDateTime.date;
    HQData.GetDayKLineDataBySymbol(symbol, (fullData)=>
    {
        if (date==null) 
        {
            findIndex=fullData.length-1;
        }
        else
        {
            for(var i=0;i<fullData.length;++i)
            {
                var kItem=fullData[i];
                var value=kItem[0];
                if (value>=date)
                {
                    findIndex=i;
                    break;
                }
            }
        }
            
        if (findIndex<=0)   //数据到头了
        {
            var hqchartData={ name:symbol, symbol:symbol, code:0, ver:2, data:[] };
            self.ChartSplashPaint.EnableSplash(false);
            callback(hqchartData);
            alert("数据到头了，没有数据了!!")
            return;   
        }

        var downloadCount=100;  //下载100个数据
        var startIndex=findIndex-downloadCount;
        if (startIndex<0) startIndex=0;
        var hqchartData={ name:symbol, symbol:symbol, code:0, ver:2, data:[] };
        for(var i=startIndex; i<findIndex; ++i)
        {
            hqchartData.data.push(fullData[i]);
        }
    
        option.DataOffset=-parseInt(dataCount/2); //当前屏数据往前移动
       

        console.log('[HQData::RequestDragDayData] ', hqchartData);

        if (HQData.IsNonEmptyArray(aryOverlay))
        {
            hqchartData.overlay=[];
            var startDate=hqchartData.data[0][0];
            var endDate=hqchartData.data[hqchartData.data.length-1][0];
            for(var i=0;i<aryOverlay.length;++i)
            {
                var item=aryOverlay[i];
                HQData.GetDayKLineDataBySymbol(item.symbol, (overlayFullData, code)=>
                {
                    var aryData=HQData.GetKLineDataByDate(overlayFullData, startDate, endDate);
                    hqchartData.overlay.push({ symbol:code, name:code, data:aryData});

                    if (hqchartData.overlay.length==aryOverlay.length)
                    {
                        self.ChartSplashPaint.EnableSplash(false);
                        callback({data:hqchartData});
                    }
                });
                
            }
        }
        else
        {
            self.ChartSplashPaint.EnableSplash(false);
            callback({data:hqchartData});
        }
    });

}


HQData.RequestDragMinuteData=function (data, callback) 
{
    data.PreventDefault=true;
    var dataCount=data.Option.XShowCount;
    var symbol=data.Request.Data.symbol;        //请求的股票代码
    var firstDateTime=data.Request.Data.first;
    var aryOverlay=data.Request.Data.overlay;   //叠加股票

    console.log(`[HQData::RequestDragMinuteData] Symbol=${symbol} date=${firstDateTime.date} time=${firstDateTime.time}`);

    var self=data.Self;
    self.IsOnTouch = false;
    self.LastMovePoint=null;
    var option=data.Option;
    var title=`拖动下载数据中...... 起始位置 ${firstDateTime.date} ${firstDateTime.time}, 下载数据个数${dataCount}`
    self.EnableSplashScreen({ Title:title, Draw:true });

   
    HQData.GetM1KLineDataBySymbol(symbol, (fullData)=>
    {
        var findIndex=-1;
        if (firstDateTime.date==null)
        {
            findIndex=fullData.length-1;
        }
        else
        {
            var dateTime=firstDateTime.date*10000+firstDateTime.time;
            for(var i=0;i<fullData.length;++i)
            {
                var kItem=fullData[i];
                var value=kItem[0]*10000+kItem[8];
                if (value>=dateTime)
                {
                    findIndex=i;
                    break;
                }
            }
        }
        
        if (findIndex<=0)   //数据到头了
        {
            var hqchartData={ name:symbol, symbol:symbol, code:0, ver:2, data:[] };
            self.ChartSplashPaint.EnableSplash(false);
            callback(hqchartData);
            alert("数据到头了，没有数据了!!")
            return;   
        }

        var donwloadCount=100;
        var startIndex=findIndex-donwloadCount;
        if (startIndex<0) startIndex=0;
        var hqchartData={ name:symbol, symbol:symbol, code:0, ver:2, data:[] };
        for(var i=startIndex; i<findIndex; ++i)
        {
            hqchartData.data.push(fullData[i]);
        }

        option.DataOffset=-parseInt(dataCount/2); //当前屏数据往前移动

        if (HQData.IsNonEmptyArray(aryOverlay))
        {
            hqchartData.overlay=[];
            var startDate=hqchartData.data[0][0];
            var startTime=hqchartData.data[0][8]
            var endDate=hqchartData.data[hqchartData.data.length-1][0];
            var endTime=hqchartData.data[hqchartData.data.length-1][8];
            for(var i=0;i<aryOverlay.length;++i)
            {
                var item=aryOverlay[i];
                HQData.GetM1KLineDataBySymbol(item.symbol, (overlyFullData, code)=>
                {
                    var aryData=this.GetKLineDataByDateTime(overlyFullData, startDate, startTime ,endDate, endTime);
                    hqchartData.overlay.push({ symbol:code, name:code, data:aryData});

                    if (hqchartData.overlay.length==aryOverlay.length)
                    {
                        self.ChartSplashPaint.EnableSplash(false);
                        console.log('[KLineChart::RequestDragMinuteData] ', hqchartData);
                        callback({data:hqchartData});
                    }
                });
            }
        }
        else
        {
            self.ChartSplashPaint.EnableSplash(false);
            console.log('[KLineChart::RequestDragMinuteData] ', hqchartData);
            callback({data:hqchartData});
        }

    });
    
}


HQData.GetRandomTestData=function(min, max)   //测试数据
{
    min = Math.ceil(min);
    max = Math.floor(max);
    return Math.floor(Math.random() * (max - min + 1)) + min; //含最大值，含最小值 
}

HQData.GetM1KLineDataBySymbol=function(symbol, callback)
{
    var value=symbol;
    switch(symbol)
    {
        case "000001.sh":
        case "000300.sh":
        case "399001.sz":
        case "000001.sz":
        case "600000.sh":
        case "000151.sz":
        case "399005.sz":
        case "399006.sz":
            break;
        default:
            value="000001.sh"
            break;
    }

    var url=`${TEST_URL}M1KLine/${value}.minute.kline.json`;
    JSNetwork.HttpRequest({
        url: url,
        method: "get",
        dataType: "json",
        success: function (data) 
        {
            callback(data.data.data, symbol);
        }
        });
}

HQData.GetDayKLineDataBySymbol=function(symbol, callback)
{
    var value=symbol;
    switch(symbol)
    {
        case "000001.sh":
        case "000300.sh":
        case "399001.sz":
        case "000001.sz":
        case "600000.sh":
        case "000151.sz":
        case "399005.sz":
        case "399006.sz":
            break;
        default:
            value="000001.sh"
            break;
    }

    var url=`${TEST_URL}DayKLine/${value}.day.kline.json`;

    JSNetwork.HttpRequest({
        url: url,
        method: "get",
        dataType: "json",
        success: function (data) 
        {
            callback(data.data.data, symbol);
        }
        });
}

HQData.GetKLineDataByDateTime=function(fullData, startDate, startTime, endDate, endTime)
{
    var start=startDate*10000+startTime;
    var end=endDate*10000+endTime;

    var aryData=[];
    for(var i=0;i<fullData.length;++i)
    {
        var kItem=fullData[i];
        var date=kItem[0];
        var time=kItem[8];
        var dateTime=date*10000+time;
        if (dateTime>=start && dateTime<=end)
            aryData.push(kItem);
    }

    return aryData;
}

HQData.GetKLineDataByDate=function(fullData, startDate, endDate)
{
    var aryData=[];
    for(var i=0;i<fullData.length;++i)
    {
        var kItem=fullData[i];
        var date=kItem[0];
        if (date>=startDate && date<=endDate)
            aryData.push(kItem);
    }

    return aryData;
}

HQData.GetMulitDayMinuteDataBySymbol=function(symbol, callback)
{ 
    var value=symbol;
    switch(symbol)
    {
        case "000001.sz":
        case "600000.sh":
        case "000151.sz":
            break;
        default:
            value="000151.sz";
            break;
    }

    var url=`${TEST_URL}Day5Minute/${value}.5day.minute.json`;

    JSNetwork.HttpRequest({
        url: url,
        method: "get",
        dataType: "json",
        success: function (data) 
        {
            callback(data.data.data, symbol);
        }
        });
}

HQData.GetDayMinuteDataBySymbol=function(symbol, callback)
{
    var value=symbol;
    switch(symbol)
    {
        case "000001.sz":
        case "600000.sh":
        case "000151.sz":
            break;
        default:
            value="000151.sz"
            break;
    }

    var url=`${TEST_URL}DayMinute/${value}.1day.minute.json`;

    JSNetwork.HttpRequest({
        url: url,
        method: "get",
        dataType: "json",
        success: function (data) 
        {
            callback(data.data.stock, symbol);
        }
        });
}

HQData.GetMulitDayMinuteDataByDate=function(aryDay, aryDate)
{
    var aryData=[];
    if (!HQData.IsNonEmptyArray(aryDay)) return aryData;
    
    for(var i=0;i<aryDay.length;++i)
    {
        var item=aryDay[i];
        if (aryDate.includes(item.date))
        {
            aryData.push(item);
        }
    }

    return aryData;
}


//是否是非空的数组
HQData.IsNonEmptyArray=function(ary)
{
    if (!ary) return false;
    if (!Array.isArray(ary)) return false;

    return ary.length>0;
}

/*暴露外部用的方法*/
export default
{
    HQData:HQData
}
