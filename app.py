
#from random import choices

from fastapi import Depends, FastAPI
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import pymongo
import uvicorn
from random import randint,shuffle
from datetime import date,datetime
import pandas as pd
security = HTTPBasic()
app=FastAPI()

#MongoDB Connection
client = pymongo.MongoClient("mongodb+srv://JnaneswarRao:MongoDb@cluster0.b16ec.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = client.test
db1=client["REDCARPETUP"]
coll1=db1["taxPayers"]
coll2=db1["Tax Accountants"]
coll3 = db1["Admins"]


# New Registration or not confirmation
'''
class confirm(BaseModel):
    NRN_or_TRN: str  #NRN -> New Registration , TRN -> Temporary Reference Number
 '''
'''@app.post("/confirm/{TOP}")
def Confirm(TOP:str):
    if(TOP=="NRN"):
        return {"New Registration"}
    if(TOP=="TRN"):
        return {"Old User , Temporary Reference Number is Mandatory"}
'''

#If new user Signup
@app.post("/Signup")
def Signup(TypeOfUser:str,Name:str,Password:str,Pan_Card:str,Annual_Income:float,Email:str,Mobile_Number:int,State:str):
    l=[0,1,2,3,4,5,6,7,8,9]
    Provisional_Id=""
    for i in range(1,11):
        Provisional_Id=Provisional_Id+str(randint(1,9))
    shuffle(l)

    if(TypeOfUser=="Tax Payer"):
        dict1={
                "Provisional_Id":Provisional_Id,
                "Username":Name,
                "Password":Password,
                "Pan_Card":Pan_Card,
                "Type of User":TypeOfUser,
                "State":State,
                "Income":Annual_Income,
                "E-Mail":Email,
                "Mobile_Number":Mobile_Number,
                "SGST":0.0,
                "CGST":0.0,
                "Total_Tax":0.0,
                "state_of_tax":"New"
              }
        coll1.insert_one(dict1)
    if(TypeOfUser=="Tax Accountant"):
        dict1 = {
            "Provisional_Id": Provisional_Id,
            "Username": Name,
            "Password": Password,
            "Pan_Card": Pan_Card,
            "Type of User": TypeOfUser,
            "State": State,
            "E-Mail": Email,
            "Mobile_Number": Mobile_Number
        }
        coll2.insert_one(dict1)

    if(TypeOfUser=="Admin"):
        dict1 = {
            "Provisional_Id": Provisional_Id,
            "Username": Name,
            "Password": Password,
            "Pan_Card": Pan_Card,
            "Type of User": TypeOfUser,
            "State": State,
            "E-Mail": Email,
            "Mobile_Number": Mobile_Number
        }
        coll3.insert_one(dict1)
    return {"User Successfully created and Allocated Provisional Id, Login with : "+Provisional_Id}



@app.post("/login")
def login(credentials: HTTPBasicCredentials = Depends(security)):
    Provisional_Id=credentials.Provisional_Id
    Password=credentials.password
    tod_Date = date.today()

    for j in coll1.find():
        if(j["Provisional_Id"]==Provisional_Id and j["Password"]==Password): #Tax Payer
            for i in coll1.find({"Provisional_Id":Provisional_Id}):
                Date=datetime.fromisoformat(i["New_Due_Date"])
                if(tod_Date>Date):
                    coll1.update_one({"Provisional_Id":Provisional_Id},{"$set":{"state_of_tax":"Delayed"}})
            for i in coll1.find({"Provisional_Id":Provisional_Id}):
                return i

    for j in coll2.find():
        details = []
        if (j["Provisional_Id"] == Provisional_Id and j["Password"] == Password):  # Tax Accountant
            for i in coll1.find({}):
                details.append({"TaxPayerName : " + i["Username"], "Provisional_Id : " + i["Provisional_Id"],
                                "state_of_tax : " + i["state_of_tax"]})
            return details

    for j in coll3.find():
        details=[]
        if(j["Provisional_Id"]==Provisional_Id and j["Password"]==Password): # Admin
            for i in coll1.find():
                details.append({"TaxPayerName : " + i["Username"],"Provisional_Id : " +i["Provisional_Id"],"state_of_tax : "+i["state_of_tax"]})
            for j in coll2.find():
                details.append("AccountantName : "+j["Username"])
        else:
            return {"Provisional_Id/Password is/are Incorrect"}

        return details
    return {"Provisional_Id/Password is/are Incorrect"}


@app.get("/AssigningTaxes")  # Create an authentication for it
def Taxes(Id:str,credentials: HTTPBasicCredentials = Depends(security)):
    Annual_income=0.0
    Tot_Tax=0.0
    CGST = 0.0
    SGST = 0.0
    state=""
    Provisional_Id=credentials.Provisional_Id
    password=credentials.password
    for j in coll2.find():
        if(Provisional_Id==j["Provisional_Id"] and password==j["Password"]):
            for i in coll1.find({"Provisional_Id":Id}):
                Annual_income=i["Income"]
                state=i["State"]
            Union_Teritory=["Andaman and Nicobar Islands","Chandigarh","Delhi","Jammu and Kashmir","Ladakh","Lakshadweep","Puducherry"," Dadra and Nagar Haveli","Daman and Diu"]
            if(state in Union_Teritory):
                coll1.update_one({"Provisional_Id": Id}, {"$set": {"CGST": CGST, "SGST": SGST, "Total_Tax": Tot_Tax}})
                return {"No Tax for Union_Teritory "}
            else:
                if(Annual_income<250000):
                    coll1.update_one({"Provisional_Id": Id}, {"$set": {"CGST": CGST, "SGST": SGST, "Total_Tax": Tot_Tax}})

                if(Annual_income>=250000 and Annual_income<500000):
                    CGST=Annual_income*0.025    #CGST = Applicable GST Rate / 2 (for 5%, CGST will be 5/2=2.5%)
                    SGST=Annual_income*0.025    #SGST / UTGST = Applicable GST Rate / 2 (for 5%, SGST will be 5/2=2.5%)

                if(Annual_income>=500000 and Annual_income<750000):
                    CGST = Annual_income * 0.05  # CGST = Applicable GST Rate / 2 (for 10%, CGST will be 10/2=0.05%)
                    SGST = Annual_income * 0.05  # SGST / UTGST = Applicable GST Rate / 2 (for 10%, SGST will be 10/2=0.05%)

                if(Annual_income>=750000 and Annual_income<1000000):
                    CGST = Annual_income * 0.075  # CGST = Applicable GST Rate / 2 (for 5%, CGST will be 5/2=2.5%)
                    SGST = Annual_income * 0.075 # SGST / UTGST = Applicable GST Rate / 2 (for 5%, SGST will be 5/2=2.5%)

                if(Annual_income>=1000000 and Annual_income<1250000):
                    CGST = Annual_income * 0.1  # CGST = Applicable GST Rate / 2 (for 5%, CGST will be 5/2=2.5%)
                    SGST = Annual_income * 0.1  # SGST / UTGST = Applicable GST Rate / 2 (for 5%, SGST will be 5/2=2.5%)

                if(Annual_income>=1250000 and Annual_income<1500000):
                    CGST = Annual_income * 0.125  # CGST = Applicable GST Rate / 2 (for 5%, CGST will be 5/2=2.5%)
                    SGST = Annual_income * 0.125  # SGST / UTGST = Applicable GST Rate / 2 (for 5%, SGST will be 5/2=2.5%)

                if(Annual_income>=1500000):
                    CGST = Annual_income * 0.15  # CGST = Applicable GST Rate / 2 (for 5%, CGST will be 5/2=2.5%)
                    SGST = Annual_income * 0.15  # SGST / UTGST = Applicable GST Rate / 2 (for 5%, SGST will be 5/2=2.5%)

            Tot_Tax = CGST + SGST
            coll1.update_one({"Provisional_Id": Id}, {"$set": {"CGST": CGST, "SGST": SGST, "Total_Tax": Tot_Tax}})
            return {"Successfully added tax to " + Id}

@app.get("/Pay_Tax")
def Pay_Tax(Pay_Amount:float,credentials: HTTPBasicCredentials = Depends(security)):
    Id=credentials.Provisional_Id
    Password=credentials.password
    for j in coll1.find():
        if(j["Provisional_Id"]==Id and j["Password"]==Password):
            for i in coll1.find({"Provisional_Id":Id}):
                Tax=i["Total_Tax"]
                Total_Tax=Tax-Pay_Amount
                CGST=Total_Tax/2
                SGST=Total_Tax/2
                Date=date.today()
                new_date = Date + pd.DateOffset(months=1)
                Date=str(Date)
                coll1.update_one({"Provisional_Id": Id}, {"$set": {"CGST": CGST, "SGST": SGST, "Total_Tax": Total_Tax,"Tax_Paid_Date":Date ,"Next_Due_Date":str(new_date.date()),"state_of_tax":"Paid"}})
                return {"Tax Paid Successfully And updated in Ur Account"}


if(__name__=="__main__"):
    uvicorn.run("Main:app")

