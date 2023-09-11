
from flask import Flask, render_template, request, redirect, session
import os
from time import time
from wallet import Wallet
from wallet import Account
import firebase_admin
from firebase_admin import credentials

STATIC_DIR = os.path.abspath('static')

app = Flask(__name__, static_folder=STATIC_DIR)
app.use_static_for_root = True

myWallet =  Wallet()
account = None
allAccounts = []
user= None
# 1.1 Create isSignedIn flag variable that tells if user is signed in or not and set it to false initially


def firebaseInitialization():
    cred = credentials.Certificate("config/serviceAccountKey.json")
    firebase_admin.initialize_app(cred, {'databaseURL': 'https://blockchain-wallet-a2812-default-rtdb.firebaseio.com'})
    print("🔥🔥🔥🔥🔥 Firebase Connected! 🔥🔥🔥🔥🔥")

firebaseInitialization()

@app.route("/", methods= ["GET", "POST"])
def home():
    global myWallet, account, allAccounts, isSignedIn
    isConnected = myWallet.checkConnection()
    balance = "No Balance"
    transactions = None
   
    # 1.1 Check if user is signed in and only then perform the following tasks
    
    # Do these if isSignedIn is true
    allAccounts = myWallet.getAccounts()
    if(account == None and allAccounts):
        account = allAccounts[0]
    
    if(account):
        if(type(account) == dict):
            balance = myWallet.getBalance(account['address'])
            transactions = myWallet.getTransactions(account['address'])
        else:
            balance = myWallet.getBalance(account.address)
            transactions = myWallet.getTransactions(account.address)
    # Till here

    # 1.1 Pass isSignedIn as isSignedIn parameter
    return render_template('index.html', 
                        isConnected=isConnected,  
                        account= account, 
                        balance = balance, 
                        transactions = transactions, 
                        allAccounts=allAccounts)

@app.route("/makeTransaction", methods = ["GET", "POST"])
def makeTransaction():
    global myWallet, account

    sender = request.form.get("senderAddress")
    receiver = request.form.get("receiverAddress")
    amount = request.form.get("amount")

    senderType = 'ganache'
    privateKey = None
    if(type(account) == dict):
       if(sender == account['address']):
            senderType = 'newAccountAddress'
            privateKey = account['privateKey']
    else:
        if(sender == account.address):
            senderType = 'newAccountAddress'
            privateKey = account.privateKey
    

    tnxHash = myWallet.makeTransactions(sender, receiver, amount, senderType, privateKey)
    myWallet.addTransactionHash(tnxHash, sender, receiver, amount)
    return redirect("/")


@app.route("/createAccount", methods= ["GET", "POST"])
def createAccount(): 
    global account, myWallet
    
    return redirect("/")

@app.route("/changeAccount", methods= ["GET", "POST"])
def changeAccount(): 
    global account, allAccounts
    
    newAccountAddress = int(request.args.get("address"))
    account = allAccounts[newAccountAddress]
    return redirect("/")

@app.route("/signIn", methods= ["GET", "POST"])
def signIn(): 
    # 1.1 Access isSignedIn as global
    global myWallet, isSignedIn
    
    username = request.form.get("user")
    password = request.form.get("password")
    
    # 1.1 Call the addUser method with username and password and store the results back in isSignedIn variable
    isSignedIn = myWallet.addUser(username, password)
    
    return redirect("/")

@app.route("/signOut", methods= ["GET", "POST"])
def signOut(): 
    # 1.1 Access isSignedIn global variable
    global isSignedIn
    # 1.1 Set isSignedIn to false
    isSignedIn = False
    
    return redirect("/")

if __name__ == '__main__':
    app.run(debug = True, port=4000)

