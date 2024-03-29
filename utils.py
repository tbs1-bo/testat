def gym_grading(percent):
    '''
    return Gymnasium grading from the given percentage
        Source: https://www.kmk.org/fileadmin/Dateien/pdf/Bildung/AllgBildung/176_Vereinb-S-II-Abi_2021-02-18.pdf
    (page 23)
    100-95	0,7
    94-90	1
    89-85   1,3
    84-80	1,7
    79-75	2
    74-70	2,3
    69-65	2,7
    64-60	3
    59-55	3,3
    54-50	3,7
    49-45	4
    44-40	4,3
    39-33	4,7
    32-27	5
    26-20	5,3
    19-0	6
    '''
    if percent >= 95: return 0.7
    elif percent >= 90: return 1
    elif percent >= 85: return 1.3
    elif percent >= 80: return 1.7
    elif percent >= 75: return 2
    elif percent >= 70: return 2.3
    elif percent >= 65: return 2.7
    elif percent >= 60: return 3
    elif percent >= 55: return 3.3
    elif percent >= 50: return 3.7
    elif percent >= 45: return 4
    elif percent >= 40: return 4.3
    elif percent >= 33: return 4.7
    elif percent >= 27: return 5
    elif percent >= 20: return 5.3
    else: return 6


def ihk_grading(percent):
    'return the IHK grading from the given percentage'

    PERCENTAGE_TO_GRADE = {
        0:	6.0,
        1:	6.0,
        2:	6.0,
        3:	6.0,
        4:	6.0,
        5:	6.0,
        6:	5.9,
        7:	5.9,
        8:	5.9,
        9:	5.9,
        10:	5.9,
        11:	5.9,
        12:	5.8,
        13:	5.8,
        14:	5.8,
        15:	5.8,
        16:	5.8,
        17:	5.7,
        18:	5.7,
        19:	5.7,
        20:	5.7,
        21:	5.7,
        22:	5.7,
        23:	5.6,
        24:	5.6,
        25:	5.6,
        26:	5.6,
        27:	5.6,
        28:	5.6,
        29:	5.5,
        30:	5.4,
        31:	5.4,
        32:	5.3,
        33:	5.3,
        34:	5.2,
        35:	5.2,
        36:	5.1,
        37:	5.1,
        38:	5.0,
        39:	5.0,
        40:	5.0,
        41:	4.9,
        42:	4.9,
        43:	4.8,
        44:	4.8,
        45:	4.7,
        46:	4.7,
        47:	4.6,
        48:	4.6,
        49:	4.5,
        50:	4.4,
        51:	4.4,
        52:	4.3,
        53:	4.3,
        54:	4.2,
        55:	4.2,
        56:	4.1,
        57:	4.0,
        58:	4.0,
        59:	3.9,
        60:	3.9,
        61:	3.8,
        62:	3.7,
        63:	3.7,
        64:	3.6,
        65:	3.6,
        66:	3.5,
        67:	3.4,
        68:	3.3,
        69:	3.3,
        70:	3.2,
        71:	3.1,
        72:	3.1,
        73:	3.0,
        74:	2.9,
        75:	2.9,
        76:	2.8,
        77:	2.7,
        78:	2.7,
        79:	2.6,
        80:	2.5,
        81:	2.4,
        82:	2.3,
        83:	2.2,
        84:	2.1,
        85:	2.0,
        86:	2.0,
        87:	1.9,
        88:	1.8,
        89:	1.7,
        90:	1.6,
        91:	1.5,
        92:	1.4,
        93:	1.4,
        94:	1.3,
        95:	1.3,
        96:	1.2,
        97:	1.2,
        98:	1.1,
        99:	1.1,
        100:1.0
    }

    return PERCENTAGE_TO_GRADE[percent]
    