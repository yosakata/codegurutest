



hex_dict = {
    "1": "1",
    "2": "2",
    "3": "3",
    "4": "4",
    "5": "5",
    "6": "6",
    "7": "7",
    "8": "8",
    "9": "9",
    "10": "a",
    "11": "b",
    "12": "c",
    "13": "d",
    "14": "e",
    "15": "f"
}



def binary2decimal(num):
    digits = list(str(num))
    sum = 0
    for i in range(len(binary)):
        sum += int(digits[-(i+1)])*2**i
    print(sum)

def decimal2hex(num):
    if str(num) in hex_dict:
        print(hex_dict[str(num)])
    else:
        print(f"{num} is invalid")

binary = "1011111111"
decimal2hex(15)
decimal2hex(18)
binary2decimal(binary)



