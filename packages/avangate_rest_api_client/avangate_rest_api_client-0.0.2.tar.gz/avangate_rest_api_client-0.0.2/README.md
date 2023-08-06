# Avangate Rest API Client

Python API client for the Avangate service.

# Example

#### Retrieve an order

Retrieve details on a specific order using its unique, system generated reference.


```python
import requests
from avangate_rest_api_client import Client

try:
    client = Client(merchant_code='MERCHANT_CODE', api_secret_key='API_SECRET_KEY')
    client.set_base_url(base_url='https://api.avangate.com/rest/3.0/')
    request = client.get('orders/111111/')
    print(request.json())
except requests.RequestException as e:
    print("Failed to send requests: {}".format(e))
```

#### Output

```python
{
   'RefNo':'111111',
   'OrderNo':1,
   'ExternalReference':None,
   'ShopperRefNo':None,
   'Status':'COMPLETE',
   'ApproveStatus':'OK',
   'VendorApproveStatus':'OK',
   'Language':'en',
   'OrderDate':'2018-04-23 15:41:47',
   'FinishDate':'2018-04-23 15:49:22',
   'Source':None,
   'AffiliateSource':None,
   'AffiliateId':None,
   'AffiliateName':None,
   'AffiliateUrl':None,
   'RecurringEnabled':False,
   'HasShipping':False,
   'BillingDetails':{
      'FiscalCode':None,
      'Phone':None,
      'FirstName':'Onur',
      'LastName':'Salgit',
      'Company':None,
      'Email':'mail+test@onur.org',
      'Address1':'Sogutozu Mah.',
      'Address2':'',
      'City':'Ankara',
      'Zip':'06370',
      'CountryCode':'tr',
      'State':'Ankara'
   },
   'DeliveryDetails':{
      'Phone':None,
      'FirstName':'Onur',
      'LastName':'Salgit',
      'Company':None,
      'Email':'mail+test@onur.org',
      'Address1':'Sogutozu mah.',
      'Address2':'',
      'City':'Ankara',
      'Zip':'06370',
      'CountryCode':'tr',
      'State':'Ankara'
   },
   'PaymentDetails':{
      'Type':'CC',
      'Currency':'try',
      'PaymentMethod':{
         'FirstDigits':'4812',
         'LastDigits':'3195',
         'CardType':'visa',
         'RecurringEnabled':False,
         'InstallmentsNumber':None
      },
      'CustomerIP':'127.0.0.1'
   },
   'CustomerDetails':None,
   'Origin':'Web',
   'AvangateCommission':10.1,
   'OrderFlow':'REGULAR',
   'GiftDetails':None,
   'PODetails':None,
   'ExtraInformation':{
      'PaymentLink':'#'
   },
   'PartnerCode':None,
   'PartnerMargin':None,
   'PartnerMarginPercent':None,
   'ExtraMargin':None,
   'ExtraMarginPercent':None,
   'ExtraDiscount':None,
   'ExtraDiscountPercent':None,
   'LocalTime':None,
   'TestOrder':False,
   'Errors':None,
   'Items':[
      {
         'ProductDetails':{
            'Name':'Test Product',
            'ExtraInfo':None,
            'RenewalStatus':False,
            'Subscriptions':[
               {
                  'SubscriptionReference':'1661215107C',
                  'PurchaseDate':'2018-04-23 15:47:09',
                  'SubscriptionStartDate':'2018-04-23 15:47:09',
                  'ExpirationDate':'2018-05-23 15:47:09',
                  'Lifetime':False,
                  'Trial':False,
                  'Enabled':True,
                  'RecurringEnabled':False
               }
            ]
         },
         'PriceOptions':[

         ],
         'Price':{
            'UnitNetPrice':0.03,
            'UnitGrossPrice':0.04,
            'UnitVAT':0.01,
            'UnitDiscount':0,
            'UnitNetDiscountedPrice':0.03,
            'UnitGrossDiscountedPrice':0.04,
            'UnitAffiliateCommission':0,
            'Currency':'try',
            'NetPrice':0.03,
            'GrossPrice':0.04,
            'NetDiscountedPrice':0.03,
            'GrossDiscountedPrice':0.04,
            'Discount':0,
            'VAT':0.01,
            'AffiliateCommission':0
         },
         'Code':'testproduct',
         'Quantity':1,
         'SKU':None,
         'CrossSell':None,
         'Trial':None,
         'AdditionalFields':None,
         'Promotion':None
      }
   ],
   'Promotions':[

   ],
   'AdditionalFields':None,
   'Currency':'try',
   'NetPrice':0.03,
   'GrossPrice':0.04,
   'NetDiscountedPrice':0.03,
   'GrossDiscountedPrice':0.04,
   'Discount':0,
   'VAT':0.01,
   'AffiliateCommission':0
}
```

## License

Avangate REST API Client is currently licensed under the MIT License.



[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
