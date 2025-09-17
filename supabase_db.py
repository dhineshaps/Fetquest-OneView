from supabase import create_client, Client
import bcrypt
from postgrest.exceptions import APIError

url="https://anpufhhyswexjgwwddcy.supabase.co"
key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFucHVmaGh5c3dleGpnd3dkZGN5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDM4NzM2ODEsImV4cCI6MjA1OTQ0OTY4MX0.aP4NCS53RezlAsBvAxmzqKUFYtL8azVRbsKnnGCTWmk"

supabase: Client = create_client(url, key)

try:     
    response = (
        supabase.table("fet_portfolio")
        .select("*")
        .execute()
    )
except:
    print("error in connecting")

print(response.data[0]['username'])

if not response.data:
    print("it is empty")
    response = (
    supabase.table("fet_portfolio")
    .insert({"username": "Dhinesh", "asset": "Stock","quantity":15,"average_price":652})
    .execute()
     )

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

user_name = "Dhinesh1d"
pwd="Trendset@15"
email = "dhineshpazanisamy1@gmail.com"

hash_pwd =  hash_password(pwd)
try:
    ins_response = (
        supabase.table("fet_portfolio_users")
            .insert({"username": user_name, "password_hash": hash_pwd ,"email":email})
            .execute()
    )
except APIError as e:
    print(f"{e.message.split(" ")[-1].split("_")[-2].upper()} already exits, try to login with it.")

# try:     
#     ret_pwd = (
#         supabase.table("fet_portfolio_users")
#         .select("password_hash").eq("email", email).execute()
#     )
# except:
#     print("error in connecting")



# def check_password(password: str, hashed: str) -> bool:
#     return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))

# if not ret_pwd.data:
#     print("user is not registered")
# else:
#     print("user is registered")
#     pwd_val = ret_pwd.data[0]['password_hash']
#     print(pwd_val)
#     val = check_password(pwd, pwd_val)
#     print(val)