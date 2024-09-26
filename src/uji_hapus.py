def match_case(decimal):
    match decimal:
        case '0':
            return "000"
        case '1':
            return "001"
        case '2':
            return "010"
        case '3':
            return "011"
        case '4':
            return "100"
        case '5':
            return "101"
        case '6':
            return "110"
        case '7':
            return "111"
        case _:
            return "NA"
        
print (match_case (2.15))