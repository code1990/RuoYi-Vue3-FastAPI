<template>
	
	<!--  #ifdef  H5 -->
	<div class='kline' v-bind:id='KLineID' v-bind:style="{width: ChartWidth+'px', height: ChartHeight+'px'}" ref='kline'></div>
	<!--  #endif -->
	
	<!--  #ifdef  MP-WEIXIN -->
	<canvas class="kline" v-bind:id='KLineID' type="2d"  
		v-bind:style="{width: ChartWidth+'px', height: ChartHeight+'px'}"
	    @touchstart="KLineTouchStart" @touchmove='KLineTouchMove' @touchend='KLineTouchEnd' />
	<!--  #endif -->
	
	<!--  #ifndef  H5 || MP-WEIXIN -->
	<canvas v-bind:id='KLineID' v-bind:canvas-id='KLineID' class='kline2' v-bind:style="{width: ChartWidth+'px', height: ChartHeight+'px'}" 
		  @touchstart="KLineTouchStart" @touchmove='KLineTouchMove' @touchend='KLineTouchEnd' ></canvas>  
	
	<!--  #endif -->
	
</template>

<script>
	
/*
    copyright (c) 2018 jones

    http://www.apache.org/licenses/LICENSE-2.0

    开源项目 https://github.com/jones2000/HQChart

    jones_2000@163.com

    HQChart简单的模板类
*/
	
// #ifdef H5
import HQChart from '@/vendor/hqchart/umychart.uniapp.h5'
// #endif
	
// #ifndef H5
import {JSCommon} from '@/vendor/hqchart/uniapp/umychart.wechat.3.0.js'
import {JSCommonHQStyle} from '@/vendor/hqchart/uniapp/umychart.style.wechat.js'
import {JSConsole} from '@/vendor/hqchart/uniapp/umychart.console.wechat.js'

//禁用日志
JSConsole.Complier.Log=()=>{ };
JSConsole.Chart.Log=()=>{ };
// #endif


//插件帮助函数
function HQChartHelper() { }
//把Vue3的markRow包装下，支持vue2
HQChartHelper.MarkRaw=function(value)
{
	return value;
}

// #ifdef VUE3
HQChartHelper.MarkRaw=function(value)
{
	return markRaw(value);
}
// #endif

function DefaultData() { }

DefaultData.GetKLineOption = function () 
{
    let data = 
    {
        Type: '历史K线图', 
        
        Windows: //窗口指标
        [
            {Index:"MA",Modify: false, Change: false}, 
			{Index:"VOL",Modify: false, Change: false},
			//{Index:"AMO",Modify: false, Change: false}
			/*
            { 
				Index:'多线段指标',Modify: false, Change: false,
				API: 
				{
					Name:'多线段指标',
					Script:null,
					Args:null, 
					Url:'http://127.0.0.1:18080/api/jsindex' 
				} 
			}
			*/
        ], 
 
		IsAutoUpdate:true,
        IsCorssOnlyDrawKLine:true,
        CorssCursorTouchEnd:true,
		IsClickShowCorssCursor:true,
		CorssCursorInfo:{ Left:2, Right:2, Bottom:1, IsShowCorss:true},  //十字光标刻度设置
		//IsFullDraw:true,
 
        Border: //边框
        {
            Left:   1,
            Right:  1, //右边间距
            Top:    25,
            Bottom: 25,
        },
 
        KLine:
        {
			DragMode:1, 
            Right:1,                            //复权 0 不复权 1 前复权 2 后复权
            Period:0,                           //周期: 0 日线 1 周线 2 月线 3 年线 
            PageSize:6,
            IsShowTooltip:false,
			DrawType:0, 
			DataWidth:10
        },
		
		KLineTitle:		//K线标题栏设置
		{
			DateTimeSpace:1,
			PeriodSpace:1,
			NameSpace:1,
		},
		
		ExtendChart:
		[
			{Name:'KLineTooltip' },	//开启手机端tooltip
		], 
		
		Frame:  //子框架设置
		[
		    {SplitCount:3,Custom: [{ Type: 0, Position: 'right'}]},
		    {SplitCount:2},
		    {SplitCount:3},
		],
        
    };
 
    return data;
}
 
DefaultData.GetMinuteOption=function()
{
    var option= 
    {
        Type:'分钟走势图',   //创建图形类型
            
        Windows: //窗口指标
        [
            
        ], 
            
        IsAutoUpdate:true,       //是自动更新数据
        DayCount:1,                 //1 最新交易日数据 >1 多日走势图
        IsShowRightMenu:false,       //是否显示右键菜单
        CorssCursorTouchEnd:true,
		IsClickShowCorssCursor:true,
		//IsFullDraw:true,
		
        MinuteLine:
        {
            //IsDrawAreaPrice:false,      //是否画价格面积图
        },
 
        Border: //边框
        {
            Left:1,    //左边间距
            Right:1,   //右边间距
            Top:20,
            Bottom:20
        },
            
        Frame:  //子框架设置
        [
            {SplitCount:3},
            {SplitCount:2},
            {SplitCount:3},
        ],
 
        ExtendChart:    //扩展图形
        [
            {Name:'MinuteTooltip' }  //手机端tooltip
        ],
    };
 
    return option;
}

DefaultData.CreateGuid=function()
{
	function S4()
	{
	   return (((1+Math.random())*0x10000)|0).toString(16).substring(1);
	}
	
	return "guid" + (S4()+S4()+"-"+S4()+"-"+S4()+"-"+S4()+"-"+S4()+S4()+S4());
}

var g_JSChart=new Map();

export default 
{
	name:"HQChartControl",
	
	props: 
	[
		'DefaultSymbol',
		'DefaultChart'
	],
	
	
	data() 
	{
		let data=
		{
			Symbol:'600000.sh',
			ChartWidth:550,
			ChartHeight:1000,
			KLineID:"HQChart_"+DefaultData.CreateGuid(),
			
			KLine:
			{
				Option:DefaultData.GetKLineOption(),
			},
			
			Minute:
			{
				Option:DefaultData.GetMinuteOption(),
			},
			
			ChartType:"Minute",
			
			CanvasNode:null,
		};
		
		return data;
	},
	
	created()
	{
		if (this.DefaultSymbol) this.Symbol=this.DefaultSymbol; //默认股票
		if (this.DefaultChart) 
		{
			//TODO:默认天数，周期在这里加
			if (this.DefaultChart.Type=='Minute') 
			{
				this.ChartType="Minute";
			}
			else 
			{
				this.ChartType="KLine";
			}
		}
	},
	
	methods:
	{
		SetSize(width, height)
		{
			this.ChartWidth=width;
			this.ChartHeight=height;
		},
		
		GetJSChart()
		{
			if (g_JSChart.has(this.KLineID)) return g_JSChart.get(this.KLineID);
			
			return null;
		},
		
		SetJSChart(jsChart)
		{
			g_JSChart.set(this.KLineID,jsChart)
		},
		
		ClearChart()
		{
			console.log("[ClearChart] clear");
			var jsChart=this.GetJSChart();
			if (jsChart)
			{
				jsChart.ChartDestory();
				this.SetJSChart(null);
			}
			
			// #ifdef H5
			var divKLine=document.getElementById(this.KLineID);
			while (divKLine.hasChildNodes()) 
			{
				divKLine.removeChild(divKLine.lastChild);
			}　
			// #endif
		},
		
		OnSize(option)
		{
			// #ifdef H5
			this.OnSize_h5(option);
			// #endif
			
			// #ifndef H5
			this.OnSize_app(option);
			// #endif
		},
		
		OnSize_h5(option)
		{
			var chartHeight = this.ChartHeight;
			var chartWidth = this.ChartWidth;
			 
			var kline=this.$refs.kline;
			kline.style.width=chartWidth+'px';
			kline.style.height=chartHeight+'px';
			
			var jsChart=this.GetJSChart();
			if (jsChart) jsChart.OnSize(option);
		},
		
		OnSize_app(option)
		{
			var jsChart=this.GetJSChart();
			if (jsChart)
			{
				jsChart.CanvasElement.Width=this.ChartWidth;
				jsChart.CanvasElement.Height=this.ChartHeight;
				jsChart.OnSize(option);
			}			
		},
		
		SetHQChartStyle()
		{
			// #ifdef H5
			this.SetHQChartStyle_h5();
			// #endif
			
			// #ifndef H5
			this.SetHQChartStyle_app();
			// #endif
			
		},
		
		SetHQChartStyle_h5()
		{
			var blackStyle=HQChart.HQChartStyle.GetStyleConfig(HQChart.STYLE_TYPE_ID.BLACK_ID);
			HQChart.JSChart.SetStyle(blackStyle);
			//this.$refs.kline.style.backgroundColor=blackStyle.BGColor;	//div背景色设置黑色
		},
		
		SetHQChartStyle_app()
		{
			var blackStyle=JSCommonHQStyle.GetStyleConfig(JSCommonHQStyle.STYLE_TYPE_ID.BLACK_ID);
			JSCommon.JSChart.SetStyle(blackStyle);
		},
		
		CreateHQChart()
		{
			this.SetHQChartStyle();
			
			if (this.ChartType=="Minute") 
				return this.CreateMinuteChart();
			else 
				return this.CreateKLineChart();
		},
		
		CreateKLineChart_h5()  //创建K线图
		{
		    this.ClearChart();
			
			var chart=HQChart.JSChart.Init(this.$refs.kline);
			
		    this.KLine.Option.Symbol=this.Symbol;
			this.KLine.Option.NetworkFilter=this.NetworkFilter;
			
		    chart.SetOption(this.KLine.Option);
			
		    this.SetJSChart(chart);
			
			return chart;
		},
		
		CreateKLineChart_app()
		{
			this.ClearChart();
			
			var element = new JSCommon.JSCanvasElement();
			// #ifdef APP-PLUS
			element.IsUniApp=true;	//canvas需要指定下 是uniapp的app
			// #endif
			element.ID = this.KLineID;
			element.Height = this.ChartHeight;  //高度宽度需要手动绑定!!
			element.Width = this.ChartWidth;
				
			var chart = JSCommon.JSChart.Init(element);
			this.KLine.Option.NetworkFilter=this.NetworkFilter;
			this.KLine.Option.Symbol=this.Symbol;
			//this.KLine.Option.IsClickShowCorssCursor=true;
			this.KLine.Option.IsFullDraw=true; 	//每次手势移动全屏重绘
			chart.SetOption(this.KLine.Option);
			
			this.SetJSChart(chart);
			
			return chart;
		},
		
		CreateKLineChart_WeChat()
		{
			this.ClearChart();
			
			var id=`#${this.KLineID}`;
			wx.createSelectorQuery().in(this)
				.select(id)
				.fields({
					node: true,
					size: true,
				})
				.exec((res)=>
				{
					console.log("[HQChartControl::CreateKLineChart_WeChat] 2")
					this.CanvasNode= HQChartHelper.MarkRaw(res[0]);
					var element = new JSCommon.JSCanvasElement();
					element.ID = this.KLineID;
					element.CanvasNode =this.CanvasNode;
					element.Height = this.ChartHeight;  //高度宽度需要手动绑定!!
					element.Width = this.ChartWidth;
			
					console.log("[HQChartControl::CreateKLineChart_WeChat] 3",this.ChartHeight,this.ChartWidth, res)
			
					var chart = JSCommon.JSChart.Init(element); //把画布绑定到行情模块中
					this.KLine.Option.NetworkFilter=this.NetworkFilter;
					this.KLine.Option.Symbol=this.Symbol;
					//this.KLine.Option.IsClickShowCorssCursor=true;
					this.KLine.Option.IsFullDraw=true; 	//每次手势移动全屏重绘
					chart.SetOption(this.KLine.Option);
	
					this.SetJSChart(chart);				   
				});
		},
		
		CreateKLineChart()
		{
			this.ChartType="KLine";
			
			// #ifdef H5
			return this.CreateKLineChart_h5();
			// #endif
			
			//  #ifdef MP-WEIXIN
			return this.CreateKLineChart_WeChat();
			// #endif
			
			// #ifndef H5 || MP-WEIXIN
			return this.CreateKLineChart_app();
			// #endif
		},
		
		CreateMinuteChart_h5() //创建日线图
		{
			this.ClearChart();
			
			var chart=HQChart.JSChart.Init(this.$refs.kline);
			this.Minute.Option.Symbol=this.Symbol;
			this.Minute.Option.NetworkFilter=this.NetworkFilter;
			chart.SetOption(this.Minute.Option);
			
			this.SetJSChart(chart);
			
			return chart;
		},
		
		CreateMinuteChart_app()
		{
			this.ClearChart();
			
			var element = new JSCommon.JSCanvasElement();
			// #ifdef APP-PLUS
			element.IsUniApp=true;	//canvas需要指定下 是uniapp的app
			// #endif
			element.ID = this.KLineID;
			element.Height = this.ChartHeight;  //高度宽度需要手动绑定!!
			element.Width = this.ChartWidth;
					
			var chart = JSCommon.JSChart.Init(element);
			
			this.Minute.Option.NetworkFilter=this.NetworkFilter;
			this.Minute.Option.Symbol=this.Symbol;
			this.Minute.Option.IsFullDraw=true; 	//每次手势移动全屏重绘
			chart.SetOption(this.Minute.Option);
			
			this.SetJSChart(chart);
			
			return chart;
		},
		
		CreateMinuteChart_WeChat()
		{
			this.ClearChart();
			
			var id=`#${this.KLineID}`;
			wx.createSelectorQuery().in(this)
				.select(id)
				.fields({
					node: true,
					size: true,
				})
				.exec((res)=>
				{
					this.CanvasNode= HQChartHelper.MarkRaw(res[0]);
					var element = new JSCommon.JSCanvasElement();
					element.ID = this.KLineID;
					element.CanvasNode =this.CanvasNode;
					element.Height = this.ChartHeight;  //高度宽度需要手动绑定!!
					element.Width = this.ChartWidth;
			
					console.log("[HQChartControl::CreateMinuteChart_WeChat] 3",this.ChartHeight,this.ChartWidth, res)
			
					var chart = JSCommon.JSChart.Init(element); //把画布绑定到行情模块中
					this.Minute.Option.NetworkFilter=this.NetworkFilter;
					this.Minute.Option.Symbol=this.Symbol;
					this.Minute.Option.IsFullDraw=true; 	//每次手势移动全屏重绘
					chart.SetOption(this.Minute.Option);
				
					this.SetJSChart(chart);				   
				});
		},
		
		CreateMinuteChart()
		{
			this.ChartType="Minute";
			
			// #ifdef H5
			return this.CreateMinuteChart_h5();
			// #endif
			
			//  #ifdef MP-WEIXIN
			return this.CreateMinuteChart_WeChat();
			// #endif
			
			// #ifndef H5 || MP-WEIXIN
			return this.CreateMinuteChart_app();
			// #endif
		},
		
		IsKLineChart()
		{
			var jsChart=this.GetJSChart();
			if (!jsChart) return false;
			var className=jsChart.JSChartContainer.ClassName;
			if (className=="KLineChartContainer" || className=="KLineChartHScreenContainer") return true;
			
			return false;
		},
		
		IsMinuteChart()
		{
			var jsChart=this.GetJSChart();
			if (!jsChart) return false;
			var className=jsChart.JSChartContainer.ClassName;
			if (className=="MinuteChartContainer" || className=="MinuteChartHScreenContainer") return true;
			
			return false;
		},
		
		//K线周期切换
		ChangeKLinePeriod(period)
		{
			var jsChart=this.GetJSChart();
			this.KLine.Option.KLine.Period=period;
			if (this.IsKLineChart() && jsChart)
			{
				jsChart.ChangePeriod(period);
			}
			else
			{
				this.CreateKLineChart();
			}
		},
		
		//走势图多日切换
		ChangeMinutePeriod(dayCount)
		{
			var jsChart=this.GetJSChart();
			this.Minute.Option.DayCount=dayCount;
			if (this.IsMinuteChart() && jsChart)
			{
				jsChart.ChangeDayCount(dayCount);
			}
			else
			{
				this.CreateMinuteChart();	//类型不对 删了重建
			}
		},
		
		//切换指标 windowId=窗口索引 name=指标名字
		ChangeKLineIndex(windowId,name)
		{
			var jsChart=this.GetJSChart();
			if (this.IsKLineChart() && jsChart) jsChart.ChangeIndex(windowId,name);
		},
		
		//切换股票
		ChangeSymbol(symbol)
		{
			this.Symbol=symbol;
			var jsChart=this.GetJSChart();
			if (jsChart) jsChart.ChangeSymbol(symbol);
		},
		
		ChangeRight(right)
		{
			var jsChart=this.GetJSChart();
			
			if (this.IsKLineChart() && jsChart)	jsChart.ChangeRight(right);
		},
		
		ChangeKLineDrawType(id)
		{
			var jsChart=this.GetJSChart();
			
			if (this.IsKLineChart() && jsChart)	jsChart.ChangeKLineDrawType(id);
		},
		
		///////////////////////////////////////////////
		//手势事件 app/小程序才有
		//KLine事件
		KLineTouchStart(event) 
		{
			var jsChart=this.GetJSChart();
			if (jsChart) 
			{
				var backup=this.ConvertTouchEventData(event);
				jsChart.OnTouchStart(event);
				this.RestoreTouchEventData(backup, event);
			}
		},
		
		KLineTouchMove (event) 
		{
			var jsChart=this.GetJSChart();
			if (jsChart) 
			{
				var backup=this.ConvertTouchEventData(event);
				jsChart.OnTouchMove(event);
				this.RestoreTouchEventData(backup, event);
			}
		},
		
		KLineTouchEnd (event) 
		{
			var jsChart=this.GetJSChart();
			if (jsChart) 
			{
				var backup=this.ConvertTouchEventData(event);
				jsChart.OnTouchEnd(event);
				this.RestoreTouchEventData(backup, event);
			}
		},
		
		ConvertTouchEventData(event)
		{
			if (Array.isArray(event.touches)) return null;
			
			var touches=event.touches;	//备份下
			var aryTouches=[];
			for(var i=0;i<10;++i)
			{
				var key=i.toString();
				var item=event.touches[key];
				if (!item) break;
				
				aryTouches[i]=item;
			}
			
			event.touches=aryTouches;
			
			var changedTouches=event.changedTouches;
			var aryChangedTouches=[];
			for(var i=0;i<10;++i)
			{
				var key=i.toString();
				var item=event.changedTouches[key];
				if (!item) break;
				
				aryChangedTouches[i]=item;
			}
			
			event.changedTouches=aryChangedTouches;
			
			//console.log('ConvertTouchEventData' ,event )
			
			return {Touches:touches, ChangedTouches:changedTouches };
		},
		
		RestoreTouchEventData(backup, event)
		{
			if (!backup) return;
			
			event.touches=backup.Touches;	//还原原来的touches结构
			event.changedTouches=backup.ChangedTouches
			
			//console.log('RestoreTouchEventData' ,event )
		},
		
		/////////////////////////////////////////////////////////////////////////////////////////
		NetworkFilter(data, callback)
		{
			console.log(`[HQChartTemplate:NetworkFilter] Name=${data.Name} Explain=${data.Explain}` );
		},
		
	},
	
}
	
	
</script>

<style>
</style>
