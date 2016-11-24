PATTERN = {
    -1: [ # reset
        0, 0, 0, 0, # LEFT
        0, 0, 0, 0, # RIGHT
        ],
    0: [ # I
        0, 0, 0, 0, # LEFT
        0, 0, 0, 0, # RIGHT
        ],
    1: [ # L
        180, 0, 0, 0, # LEFT
        90, 0, 0, 0, # RIGHT
        ],
    2: [ # r-L
        90, 0, 0, 0, # LEFT
        180, 0, 0, 0, # RIGHT
        ],
    3: [ # slash-r
        60, 0, 0, 0, # LEFT
        120, 0, 0, 0, # RIGHT
        ],
    4: [ # slash-l
        120, 0, 0, 0, # LEFT
        60, 0, 0, 0, # RIGHT
        ],
    5: [ # Koshi ni Te
        80, 0, 0, 115, # LEFT
        80, 0, 0, 115, # RIGHT
        ],
    6: [ # Y
        160, 0, 0, 0, # LEFT
        160, 0, 0, 0, # RIGHT
        ],
    7: [ # T
        90, 0, 0, 0, # LEFT
        90, 0, 0, 0, # RIGHT
        ],
    8: [ # Y
        170, 0, 0, 0, # LEFT
        170, 0, 0, 0, # RIGHT
        ],
    9: [
        # katate-up-R
        0, 0, 0, 0, # LEFT
        150, 0, 0, 0, # RIGHT
    ],
    10: [
        # katate-down-R
        0, 0, 0, 0, # LEFT
        0, 0, 0, 60, # RIGHT
    ],
    11: [
        # katate-up-L
        0, 0, 0, 0, # LEFT
        150, 0, 0, 0, # RIGHT
    ],
    12: [
        # katate-up-L
        150, 0, 0, 60, # LEFT
        0, 0, 0, 0, # RIGHT
    ],
    13: [
        # Naname-down
        0, 0, 0, 60, # LEFT
        0, 0, 0, 00, # RIGHT
    ],
}

_HOLD = {
    9: [ # X
        150, 0, 0, 60, # LEFT
        150, 0, 0, 60, # RIGHT
    ],
    10: [ # E
        0, 0, 0, 0, # LEFT
        90, 90, 0, 90, # RIGHT
    ],
    10: [ # r-E
        90, 90, 0, 90, # LEFT
        0, 0, 0, 0,    # RIGHT
    ],
    10: [ # Yabai
        0, 0, 0, 0, # LEFT
        0, 0, 90, 0, # RIGHT
    ],
    10: [ # F
        0, 0, 0, 0, # LEFT
        90, 0, 0, 90, # RIGHT
    ],
    10: [ # r-F
        90, 0, 0, 90, # LEFT
        0, 0, 0, 0, # RIGHT
    ]
}
