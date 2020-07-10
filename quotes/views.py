from django.shortcuts import render, redirect
from .models import Stock, Balance
from .forms import StockForm
from django.contrib import messages
from django.http import JsonResponse

# Create your views here.
def home(request):
    import requests
    import json

    default_value = Balance(title='Balance', amount=1500.00, pk=1)
    default_value.save()
    if request.method == 'POST':
        form = StockForm(request.POST or None)

        if form.is_valid():
            form.save()
            messages.success(request, ("Stock Has Been Added to the database"))
            return redirect('add_stock')
    else:
        ticker = Stock.objects.all()

        output = []

        for ticker_item in ticker:
            api_request = requests.get(
                "https://cloud.iexapis.com/stable/stock/" + str(ticker_item) + "/chart/5d?token=pk_1103aef826214ba59719ee614c8e8e3b&chartCloseOnly=true")

            try:
                api = json.loads(api_request.content)
                currentStockHistory = []
                for eachDay in api:
                    close = eachDay['close']
                    currentStockHistory.append(close)
                output.append({str(ticker_item): currentStockHistory})


            except Exception as e:
                api = "Error..."

    return render(request, 'home.html', {'ticker': ticker, 'output': output})

def about(request):
    return render(request, 'about.html', {})

def add_stock(request):
    import requests
    import json

    if request.method == 'POST':
        form = StockForm(request.POST or None)

        if form.is_valid():
            api_request = requests.get(
                "https://cloud.iexapis.com/stable/stock/aapl/quote?token=pk_1103aef826214ba59719ee614c8e8e3b")

            api = json.loads(api_request.content)
            latestPrice = api['latestPrice']
            quantity = form['quantity'].value()
            purchaseValue = float(latestPrice) * float(quantity)
            currentValue = Balance.objects.get(pk=1).amount
            newValue = float(purchaseValue) + float(currentValue)
            Balance.objects.filter(pk=1).update(amount=newValue)

            form.save()
            messages.success(request, ("Stock Has Been Added to the database"))
            return redirect('add_stock')


    else:
        ticker = Stock.objects.all()
        output = []
        quantities = []
        for ticker_item in ticker:

            api_request = requests.get(
                "https://cloud.iexapis.com/stable/stock/" + str(ticker_item) + "/quote?token=pk_1103aef826214ba59719ee614c8e8e3b")

            try:
                api = json.loads(api_request.content)
                api['quantity'] = Stock.objects.get(ticker=ticker_item).quantity
                output.append(api)
            except Exception as e:
                api = "Error..."

    return render(request, 'add_stock.html', {'ticker': ticker, 'output': output, 'quantities': quantities})

def delete(request, stock_id):
    import requests
    import json

    item = Stock.objects.get(pk=stock_id)

    api_request = requests.get(
        "https://cloud.iexapis.com/stable/stock/" + str(
            item.ticker) + "/quote?token=pk_1103aef826214ba59719ee614c8e8e3b")

    api = json.loads(api_request.content)
    latestPrice = api['latestPrice']
    quantity = Stock.objects.get(ticker=item.ticker).quantity
    saleValue = latestPrice * quantity
    currentValue = Balance.objects.get(pk=1).amount
    newValue = float(saleValue) + float(currentValue)
    Balance.objects.filter(pk=1).update(amount=newValue)

    item.delete()

    messages.success(request, ("Stock Deleted"))
    return redirect(delete_stock)

def delete_stock(request):
    ticker = Stock.objects.all()
    return render(request, 'delete_stock.html', {'ticker': ticker})

