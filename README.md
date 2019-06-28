# tradingview_monitor
Monitors alerts for tradingview charts
## Setup

The following items are required to build out the system for full functionality.
1. notifications/config.json  
  Input all json fields for notifications.  
2. tv_monitor.py/__init__  
  tradingview = username / password 
3. notifications/discord.py  
  discord channel + bot token

## Notifications

Email / SMS notifications
Notifcations may be sent via smtp using the smtplib.  Alternatively you could use a phone number with domain 
4538675309@vtext.com.  It is up to you to identify the carrier and domain allowed for that carrier. 
This is a workaround to implement SMS without building a separate server to facilitate forwarding 
messages to phones.

####Email setup requires:
- Source email address 
- Password 
- Destination email 
   
```
{
    "DEST_EMAIL": "",
    "EMAIL_ADDRESS": "",
    "PASSWORD": ""
}
```
#### Discord notifications
Channel ID + Bot Token
```
notification\discord.py
    channelID = "" # enable dev mode on discord, right-click on the channel, copy ID
    botToken = ""    # get from the bot page. must be a bot, not a discord app

```

#### Tradingview settings
Username + Password
```
    class TV:
        if type == 'auto':
            username = ""  #Tradingview username / email
            password = ""  #Tradingview password

```