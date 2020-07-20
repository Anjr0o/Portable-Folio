from django.shortcuts import render, redirect
from .models import Stock, Balance, Transaction
from .forms import StockForm, DeleteForm
from django.contrib import messages
from django.http import JsonResponse

# Create your views here.
def home(request):
    import requests
    import json

    balance = Balance.objects.get(pk=1).amount

    if request.method == 'POST':
        form = StockForm(request.POST or None)

        if int(form['quantity'].value()) > 0:

            if form.is_valid():
                try:
                    api_request = requests.get("https://cloud.iexapis.com/stable/stock/"+ form['ticker'].value() + "/quote?token=pk_1103aef826214ba59719ee614c8e8e3b")

                    api = json.loads(api_request.content)
                    latestPrice = api['latestPrice']
                    if Stock.objects.filter(ticker=form['ticker'].value()):
                        quantity = form['quantity'].value()
                        newQuantity = int(Stock.objects.get(ticker=form['ticker'].value()).quantity) + int(quantity)
                        Stock.objects.filter(ticker=form['ticker'].value()).update(quantity=newQuantity)
                        return redirect('add_stock')

                    else:
                        form.save()
                        messages.success(request, ("Stock Has Been Added to the database"))
                        return redirect('add_stock')
                except:
                    messages.error(request, ('Stock not Valid'))

        else:
            messages.error(request, ("Cannot add a negative quantity"))
            return redirect('add_stock')
    else:
        ticker = Stock.objects.all()

        output = []

        portfolioValueData = [0, 0, 0, 0, 0]

        for ticker_item in ticker:
            api_request = requests.get("https://cloud.iexapis.com/stable/stock/" + str(ticker_item) + "/chart/5d?token=pk_1103aef826214ba59719ee614c8e8e3b&chartCloseOnly=true")

            api = json.loads(api_request.content)
            currentStockHistory = []

            for counter, eachDay in enumerate(api):
                close = eachDay['close']
                currentStockHistory.append(close)
                quantity = Stock.objects.get(ticker=str(ticker_item)).quantity
                valueOwned = close * quantity
                totalOwned = portfolioValueData[counter] + valueOwned
                portfolioValueData[counter] = totalOwned

            output.append({str(ticker_item): currentStockHistory})


    return render(request, 'home.html', {'ticker': ticker, 'output': output, 'portfolioValueData': portfolioValueData, 'balance': balance})

def transactions(request):
    transactions = Transaction.objects.all()
    return render(request, 'transactions.html', {'transactions': transactions})

def add_stock(request):
    import requests
    import json

    if request.method == 'POST':
        form = StockForm(request.POST or None)
        if int(form['quantity'].value()) > 0:
            if form.is_valid():
            # try:
                api_request = requests.get("https://cloud.iexapis.com/stable/stock/"+ form['ticker'].value() + "/quote?token=pk_1103aef826214ba59719ee614c8e8e3b")

                api = json.loads(api_request.content)
                latestPrice = api['latestPrice']

                quantity = form['quantity'].value()
                purchaseValue = float(latestPrice) * float(quantity)
                currentValue = Balance.objects.get(pk=1).amount
                newValue = float(currentValue) - float(purchaseValue)
                Balance.objects.filter(pk=1).update(amount=newValue)

                if Stock.objects.filter(ticker=form['ticker'].value()):
                    newQuantity = int(Stock.objects.get(ticker=form['ticker'].value()).quantity) + int(quantity)
                    Stock.objects.filter(ticker=form['ticker'].value()).update(quantity=newQuantity)
                    return redirect('add_stock')

                else:
                    form.save()
                    messages.success(request, ("Stock Has Been Added to the database"))
                    return redirect('add_stock')
            # except:
                messages.error(request, ('Stock not Valid'))
                return redirect('add_stock')
        else:
            messages.error(request, ("Cannot add a negative quantity"))
            return redirect('add_stock')

    else:
        ticker = Stock.objects.all()
        output = []
        quantities = []
        for ticker_item in ticker:

            api_request = requests.get("https://cloud.iexapis.com/stable/stock/" + str(ticker_item) + "/quote?token=pk_1103aef826214ba59719ee614c8e8e3b")

            try:
                api = json.loads(api_request.content)
                api['quantity'] = Stock.objects.get(ticker=ticker_item).quantity
                output.append(api)
            except Exception as e:
                api = "Error..."

    return render(request, 'add_stock.html', {'ticker': ticker, 'output': output, 'quantities': quantities})

def reset_portfolio(request):
    default_value = Balance(title='Balance', amount=15000.00, pk=1)
    default_value.save()
    Stock.objects.all().delete()

    return redirect(delete_stock)

def delete(request, stock_id):
    import requests
    import json

    form = DeleteForm(request.POST or None)
    stock_quantity = form['quantity'].value()

    item = Stock.objects.get(pk=stock_id)

    api_request = requests.get(
        "https://cloud.iexapis.com/stable/stock/" + str(
            item.ticker) + "/quote?token=pk_1103aef826214ba59719ee614c8e8e3b")

    api = json.loads(api_request.content)
    latestPrice = api['latestPrice']

    quantity = Stock.objects.get(pk=stock_id).quantity
    if int(quantity) <= int(stock_quantity):
        stock_quantity = quantity

    if int(quantity) <= int(stock_quantity):
        item.delete()
        messages.success(request, ("Stock Sold"))
    elif int(stock_quantity) > 0:
        saleValue = float(latestPrice) * float(stock_quantity)
        currentValue = Balance.objects.get(pk=1).amount
        newValue = int(saleValue) + int(currentValue)
        Balance.objects.filter(pk=1).update(amount=newValue)
        newQuantity = int(quantity) - int(stock_quantity)
        Stock.objects.filter(pk=stock_id).update(quantity=newQuantity)
        messages.success(request, ("Stock Sold"))
    else:
        messages.error(request, ("Cannot sell a negative quantity"))

    return redirect(delete_stock)

def delete_stock(request):
    ticker = Stock.objects.all()
    return render(request, 'delete_stock.html', {'ticker': ticker})