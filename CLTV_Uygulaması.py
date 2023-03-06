####################################################################################
# CUSTOMER LIFETIME VALUE (Müşteri Yaşam Boyu Değeri)

# Aşağıdaki basamakalarla uçtan uca CLTV uygulaması gerçekleştireceğim.

# 1. Veri Hazırlama
# 2. Average Order Value (average_order_value = total_price / total_transaction)
# 3. Purchase Frequency (total_transaction / total_number_of_customers)
# 4. Repeat Rate & Churn Rate (birden fazla alışveriş yapan müşteri sayısı / tüm müşteriler)
# 5. Profit Margin (profit_margin =  total_price * 0.10)
# 6. Customer Value (customer_value = average_order_value * purchase_frequency)
# 7. Customer Lifetime Value (CLTV = (customer_value / churn_rate) x profit_margin)
# 8. Segmentlerin Oluşturulması
# 9. BONUS: Tüm İşlemlerin Fonksiyonlaştırılması


####################################################################################
# 1. Veri Hazırlama
####################################################################################

# Veri Seti Hikayesi
# https://archive.ics.uci.edu/ml/datasets/Online+Retail+II

# Online Retail II isimli veri seti İngiltere merkezli online bir satış mağazasının 01/12/2009 - 09/12/2011 tarihleri arasındaki satışlarını içeriyor.

# Değişkenler
# InvoiceNo: Fatura numarası. Her işleme yani faturaya ait eşsiz numara. C ile başlıyorsa iptal edilen işlem.
# StockCode: Ürün kodu. Her bir ürün için eşsiz numara.
# Description: Ürün ismi
# Quantity: Ürün adedi. Faturalardaki ürünlerden kaçar tane satıldığını ifade etmektedir.
# InvoiceDate: Fatura tarihi ve zamanı.
# UnitPrice: Ürün fiyatı (Sterlin cinsinden)
# CustomerID: Eşsiz müşteri numarası
# Country: Ülke ismi. Müşterinin yaşadığı ülke.


# Amacımız: CLTV' ni her bir müşteri için hesaplamak ve daha sonra CLTV'lerine göre bir segmentasyon çalışması yapmaktır.

import pandas as pd
from sklearn.preprocessing import MinMaxScaler
pd.set_option('display.width', 500)
pd.set_option('display.max_columns', None)
pd.set_option('display.float_format', lambda x: '%.5f' % x)                                                             # float sayılarının ondalık olarak 0' dan sonra kaç basamağının gösterilmesi gerektiğini ifade eden bir ayardır.

df_ = pd.read_excel("C:/Users/Emre Bilir/Desktop/DSBootcamp/crmAnalytics/datasets/online_retail_II.xlsx", sheet_name="Year 2009-2010")    # Bilgisayarımdaki ... dizininden 2009-2010 yıllarını çekiyorum.
df = df_.copy()
df.head()

# Eksik değerlere baktım.
df.isnull().sum()

# Geri iadeleri dışındaki işlemleri veri setimde tuttum.
df = df[~df["Invoice"].str.contains("C", na=False)]

# Özet istatistiklere göz atıyorum. - değerli ifadeler var.
df.describe().T

#  Problemi çözmek için Quantity değeri 0' dan büyük olan gözlem birimlerini seçip dataframe' i güncelliyorum.
df = df[(df['Quantity'] > 0)]

# İade işlemlerini silip Quantity değeri 0 olan gözlem birimlerini sildikten sonra geriye kalan eksik değer taşıyan gözlem birimlerini de siliyorum.
df.dropna(inplace=True)

# Müşterinin her faturadaki belli ürün için toplam harcadığı miktarı veri setine değişken olarak ekliyorum. Çünkü 'Price' değişkeni ürünün birim fiyatıdır. Quantity kaç adet aldığıdır.
df["TotalPrice"] = df["Quantity"] * df["Price"]

# Veri setini bu transaction datası formatından customer lifetime value' nun hesaplanması için bize lazım olan metriklere göre çevireceğim.
cltv_c = df.groupby('Customer ID').agg({'Invoice': lambda x: x.nunique(),
                                        'Quantity': lambda x: x.sum(),
                                        'TotalPrice': lambda x: x.sum()})
# Burdaik Quantity tamamen analiz etmek, gözlemlemek için yanımda götürdüğüm değerdir. Birincil önceliğim değildir. Benim için öncelik  Invoice ve total_price' dır.


# Değişkenleri yeniden tanımlıyorum.
cltv_c.columns = ['total_transaction', 'total_unit', 'total_price']
cltv_c.head()
# Artık 4314 tane müşteri var. Yani artık burdaki satırlar tekildir. Artık tabloyu CLTV hesabına uygun bir forma getirmiş oldum.


####################################################################################
# 2. Average Order Value (average_order_value = total_price / total_transaction)
####################################################################################

cltv_c["average_order_value"] = cltv_c["total_price"] / cltv_c["total_transaction"]


####################################################################################
# 3. Purchase Frequency (total_transaction / total_number_of_customers)
####################################################################################

cltv_c.head()
cltv_c["purchase_frequency"] = cltv_c["total_transaction"] / cltv_c.shape[0]


####################################################################################
# 4. Repeat Rate & Churn Rate (birden fazla alışveriş yapan müşteri sayısı / tüm müşteriler)
####################################################################################

repeat_rate = cltv_c[cltv_c["total_transaction"] > 1].shape[0] / cltv_c.shape[0]

churn_rate = 1 - repeat_rate


####################################################################################
# 5. Profit Margin (profit_margin =  total_price * 0.10)
####################################################################################

cltv_c['profit_margin'] = cltv_c['total_price'] * 0.10


####################################################################################
# 6. Customer Value (customer_value = average_order_value * purchase_frequency)
####################################################################################

cltv_c['customer_value'] = cltv_c['average_order_value'] * cltv_c["purchase_frequency"]
cltv_c.head()

####################################################################################
# 7. Customer Lifetime Value (CLTV = (customer_value / churn_rate) x profit_margin)
####################################################################################

cltv_c["cltv"] = (cltv_c["customer_value"] / churn_rate) * cltv_c["profit_margin"]


###################################################################################
# 8. Segmentlerin Oluşturulması
###################################################################################

cltv_c["segment"] = pd.qcut(cltv_c["cltv"], 4, labels=["D", "C", "B", "A"])
cltv_c.head()

# Segmentlere göre analiz yapmak için bakış atmak istedim.
cltv_c.groupby("segment").agg({"count", "mean", "sum"})

# veri setimi csv dosyasına dönüştürdüm.
cltv_c.to_csv("cltc_c.csv")


##################################################
# 9. BONUS: Tüm İşlemlerin Fonksiyonlaştırılması
##################################################

def create_cltv_c(dataframe, profit=0.10):

    # Veriyi hazırlama
    dataframe = dataframe[~dataframe["Invoice"].str.contains("C", na=False)]
    dataframe = dataframe[(dataframe['Quantity'] > 0)]
    dataframe.dropna(inplace=True)
    dataframe["TotalPrice"] = dataframe["Quantity"] * dataframe["Price"]
    cltv_c = dataframe.groupby('Customer ID').agg({'Invoice': lambda x: x.nunique(),
                                                   'Quantity': lambda x: x.sum(),
                                                   'TotalPrice': lambda x: x.sum()})
    cltv_c.columns = ['total_transaction', 'total_unit', 'total_price']
    # avg_order_value
    cltv_c['avg_order_value'] = cltv_c['total_price'] / cltv_c['total_transaction']
    # purchase_frequency
    cltv_c["purchase_frequency"] = cltv_c['total_transaction'] / cltv_c.shape[0]
    # repeat rate & churn rate
    repeat_rate = cltv_c[cltv_c.total_transaction > 1].shape[0] / cltv_c.shape[0]
    churn_rate = 1 - repeat_rate
    # profit_margin
    cltv_c['profit_margin'] = cltv_c['total_price'] * profit
    # Customer Value
    cltv_c['customer_value'] = (cltv_c['avg_order_value'] * cltv_c["purchase_frequency"])
    # Customer Lifetime Value
    cltv_c['cltv'] = (cltv_c['customer_value'] / churn_rate) * cltv_c['profit_margin']
    # Segment
    cltv_c["segment"] = pd.qcut(cltv_c["cltv"], 4, labels=["D", "C", "B", "A"])

    return cltv_c


df = df_.copy()

clv = create_cltv_c(df)
clv.head()
