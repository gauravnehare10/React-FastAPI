def userEntity(item) -> dict:
    return {
        "_id": str(item["_id"]),
        "name": item["name"],
        "username": item["username"],
        "email": item["email"],
        "contactnumber": int(item["contactnumber"])
    }

def usersEntity(items) -> list:
    return [userEntity(item) for item in items]