MODS = {
  'arr': (
    'noFail',
    'easy',
    'touchDevice',
    'hidden',
    'hardRock',
    'suddenDeath',
    'doubleTime',
    'relax',
    'halfTime',
    'nightcore',
    'flashlight',
    'autoplay',
    'spunOut',
    'autopilot',
    'perfect',
    'key4',
    'key5',
    'key6',
    'key7',
    'key8',
    'fadeIn',
    'random',
    'cinema',
    'targetPractice',
    'key9',
    'coop',
    'key1',
    'key3',
    'key2',
    'scoreV2',
    'mirror'
  ),
  'pairs': (('doubleTime', 'nightCore'), ('key4', 'key5', 'key6', 'key7', 'key8')),
  'pairNames' : ('nightCore', 'keyMod')
}

MODS_ABRV = {
  'arr': (
    'NF',
    'EZ',
    'TD',
    'HD',
    'HR',
    'SD',
    'DT',
    'RX',
    'HT',
    'NC',
    'FL',
    'AT',
    'SO',
    'AP',
    'PF',
    'K4',
    'K5',
    'K6',
    'K7',
    'K8',
    'fadeIn',
    'random',
    'CN',
    'targetPractice',
    'K9',
    'coop',
    'K1',
    'K3',
    'K2',
    'V2',
    'mirror'
  ),
  'pairs': (('DT', 'NC'), ('K4', 'K5', 'K6', 'K7', 'K8')),
  'pairNames' : ('NC', 'keyMod')
}

KEYS = {
  'arr': (
    'm1',
    'm2',
    'k1',
    'k2',
    'smoke'
  ),
  'pairs': (('k1', 'm1'), ('k2', 'm2')),
  'pairNames' : ('k1', 'k2')
}

RANKED_STATUS = (
  'unknown', 'unsubmitted', 'pending', 'unused', 'ranked', 'approved', 'qualified', 'loved'
)

MAP_FILE_SECTIONS = {
  'total': 8,
  'sectionEnd': '\n\n',
  'names': ('general', 'editor', 'metadata', 'difficulty', 'events', 'timingPoints', 'colors', 'hitobjects'),
  'headers': ('[General]\n', '[Editor]\n', '[Metadata]\n', '[Difficulty]\n', '[Events]\n', '[TimingPoints]\n', '[Colours]\n', '[HitObjects]\n'),
  'types': ('kvp', 'kvp', 'kvp', 'kvp', 'csl', 'csl', 'kvp', 'csl')
}

SKIN_ELEMENTS = {
  'approachcircle': {
    'animetable': False,
    'blendMode': 'mul',
    'origin': 'center',
    'tintType': 'combo',
    'alter': None,
    'required': True
  },
  'hitcircle': {
    'animetable': False,
    'blendMode': 'mul',
    'origin': 'center',
    'tintType': 'combo',
    'alter': None,
    'required': True
  },
  'hitcircleoverlay': {
    'animetable': False,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTint',
    'alter': None,
    'required': True
  },
  'followpoint': {
    'animetable': True,
    'blendMode': 'add',
    'origin': 'center',
    'tintType': 'noTint',
    'alter': None,
    'animationName': 'followpoint-*',
    'required': True
  },
  'lighting': {
    'animetable': False,
    'blendMode': 'add',
    'origin': 'center',
    'tintType': 'combo',
    'alter': None,
    'required': False
  },
  'sliderstartcircle': {
    'animetable': False,
    'blendMode': 'mul',
    'origin': 'center',
    'tintType': 'combo',
    'alter': 'hitcircle',
    'required': False
  },
  'sliderstartcircleoverlay': {
    'animetable': False,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTint',
    'alter': 'hitcircleoverlay',
    'required': False
  },
  'sliderendcircle': {
    'animetable': False,
    'blendMode': 'mul',
    'origin': 'center',
    'tintType': 'combo',
    'alter': 'hitcircle',
    'required': False
  },
  'sliderendcircleoverlay': {
    'animetable': False,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTint',
    'alter': 'hitcircleoverlay',
    'required': False
  },
  'reversearrow': {
    'animetable': False,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTint',
    'alter': None,
    'required': True
  },
  'sliderfollowcircle': {
    'animetable': True,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTint',
    'alter': None,
    'required': True,
    'animationName': 'sliderfollowcircle-*'
  },
  'sliderb': {
    'animetable': True,
    'blendMode': 'mul',
    'origin': 'center',
    'tintType': 'combo',
    'alter': 'sliderb-nd',
    'required': True,
    'animationName': 'sliderb*'
  },
  'sliderb-nd': {
    'animetable': False,
    'blendMode': 'mul',
    'origin': 'center',
    'tintType': 'specific',
    'tintColor': (0, 0, 0),
    'alter': None,
    'required': False
  },
  'sliderb-spec': {
    'animetable': False,
    'blendMode': 'add',
    'origin': 'center',
    'tintType': 'noTint',
    'alter': None,
    'required': False
  },
  'sliderpoint10': {
    'animetable': False,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTint',
    'alter': None,
    'required': False
  },
  'sliderpoint30': {
    'animetable': False,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTint',
    'alter': None,
    'required': False
  },
  'sliderscorepoint': {
    'animetable': False,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTint',
    'alter': None,
    'required': False
  },
  'spinner-rpm': {
    'animetable': False,
    'blendMode': 'normal',
    'origin': 'topLeft',
    'tintType': 'noTint',
    'alter': None,
    'required': False
  },
  'spinner-clear': {
    'animetable': False,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTint',
    'alter': None,
    'required': False
  },
  'spinner-spin': {
    'animetable': False,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTint',
    'alter': None,
    'required': False
  },
  'spinner-glow': {
    'animetable': False,
    'blendMode': 'add',
    'origin': 'center',
    'tintType': 'specific',
    'tintColor': {
      'default': (0, 255, 255),
      'blink': (255, 255, 255)
    },
    'alter': None,
    'required': False
  },
  'spinner-bottom': {
    'animetable': False,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTint',
    'alter': None,
    'required': False
  },
  'spinner-top': {
    'animetable': False,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTint',
    'alter': None,
    'required': False
  },
  'spinner-middle2': {
    'animetable': False,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTint',
    'alter': None,
    'required': False
  },
  'spinner-middle': {
    'animetable': False,
    'blendMode': 'mul',
    'origin': 'center',
    'tintType': 'gradient',
    'tintColor': {
      'start': (255, 255, 255),
      'end': (255, 0, 0)
    },
    'alter': None,
    'required': False
  },
  'particle50': {
    'animetable': False,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTint',
    'alter': None,
    'required': False
  },
  'particle100': {
    'animetable': False,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTint',
    'alter': None,
    'required': False
  },
  'particle300': {
    'animetable': False,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTint',
    'alter': None,
    'required': False
  },
  'cursor': {
    'animetable': False,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTint',
    'alter': None,
    'required': True
  },
  'cursormiddle': {
    'animetable': False,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTint',
    'alter': None,
    'required': False
  },
  'cursor-smoke': {
    'animetable': False,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTint',
    'alter': None,
    'required': False
  },
  'cursortrail': {
    'animetable': False,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTint',
    'alter': None,
    'required': False
  },
  'cursor-ripple': {
    'animetable': False,
    'blendMode': 'add',
    'origin': 'center',
    'tintType': 'noTint',
    'alter': None,
    'required': False
  },
  'selection-mod-autoplay': {
    'animetable': False,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTint',
    'alter': None,
    'required': False
  },
  'selection-mod-cinema': {
    'animetable': False,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTint',
    'alter': None,
    'required': False
  },
  'selection-mod-doubletime': {
    'animetable': False,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTint',
    'alter': None,
    'required': False
  },
  'selection-mod-easy': {
    'animetable': False,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTint',
    'alter': None,
    'required': False
  },
  'selection-mod-fadein': {
    'animetable': False,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTint',
    'alter': None,
    'required': False
  },
  'selection-mod-flashlight': {
    'animetable': False,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTint',
    'alter': None,
    'required': False
  },
  'selection-mod-halftime': {
    'animetable': False,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTint',
    'alter': None,
    'required': False
  },
  'selection-mod-hardrock': {
    'animetable': False,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTint',
    'alter': None,
    'required': False
  },
  'selection-mod-hidden': {
    'animetable': False,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTint',
    'alter': None,
    'required': False
  },
  'selection-mod-key1': {
    'animetable': False,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTint',
    'alter': None,
    'required': False
  },
  'selection-mod-key2': {
    'animetable': False,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTint',
    'alter': None,
    'required': False
  },
  'selection-mod-key3': {
    'animetable': False,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTint',
    'alter': None,
    'required': False
  },
  'selection-mod-key4': {
    'animetable': False,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTint',
    'alter': None,
    'required': False
  },
  'selection-mod-key5': {
    'animetable': False,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTint',
    'alter': None,
    'required': False
  },
  'selection-mod-key6': {
    'animetable': False,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTint',
    'alter': None,
    'required': False
  },
  'selection-mod-key7': {
    'animetable': False,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTint',
    'alter': None,
    'required': False
  },
  'selection-mod-key8': {
    'animetable': False,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTint',
    'alter': None,
    'required': False
  },
  'selection-mod-key9': {
    'animetable': False,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTint',
    'alter': None,
    'required': False
  },
  'selection-mod-keycoop': {
    'animetable': False,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTint',
    'alter': None,
    'required': False
  },
  'selection-mod-mirror': {
    'animetable': False,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTint',
    'alter': None,
    'required': False
  },
  'selection-mod-nightcore': {
    'animetable': False,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTint',
    'alter': None,
    'required': False
  },
  'selection-mod-nofail': {
    'animetable': False,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTint',
    'alter': None,
    'required': False
  },
  'selection-mod-perfect': {
    'animetable': False,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTint',
    'alter': None,
    'required': False
  },
  'selection-mod-random': {
    'animetable': False,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTint',
    'alter': None,
    'required': False
  },
  'selection-mod-relax': {
    'animetable': False,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTint',
    'alter': None,
    'required': False
  },
  'selection-mod-relax2': {
    'animetable': False,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTint',
    'alter': None,
    'required': False
  },
  'selection-mod-scorev2': {
    'animetable': False,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTint',
    'alter': None,
    'required': False
  },
  'selection-mod-spunout': {
    'animetable': False,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTint',
    'alter': None,
    'required': False
  },
  'selection-mod-suddendeath': {
    'animetable': False,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTint',
    'alter': None,
    'required': False
  },
  'selection-mod-target': {
    'animetable': False,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTint',
    'alter': None,
    'required': False
  },
  'selection-mod-freemodallowed': {
    'animetable': False,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTint',
    'alter': None,
    'required': False
  },
  'selection-mod-touchdevice': {
    'animetable': False,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTint',
    'alter': None,
    'required': False
  },
  'play-skip': {
    'animetable': True,
    'blendMode': 'mul',
    'origin': 'bottonRight',
    'tintType': 'noTint',
    'alter': None,
    'required': False,
    'animationName': 'play-skip-*'
  },
  'play-unranked': {
    'animetable': False,
    'blendMode': 'mul',
    'origin': 'center',
    'tintType': 'noTint',
    'alter': None,
    'required': False
  },
  'play-warningarrow': {
    'animetable': False,
    'blendMode': 'mul',
    'origin': 'center',
    'tintType': 'specific',
    'tintColor': {
      'pauseScreen': (0, 0, 255),
      'exitingBreaks': {
        'v1.0': (255, 255, 255),
        'v2.0+': (255, 0, 0)
      }
    },
    'alter': None,
    'required': False
  },
  'arrow-pause': {
    'animetable': False,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'specific',
    'tintColor': (0, 0, 255),
    'alter': ('play-warningarrow'),
    'required': False
  },
  'arrow-warning': {
    'animetable': False,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'specific',
    'tintColor': {
      'v1.0': (255, 255, 255),
      'v2.0+': (255, 0, 0)
    },
    'alter': ('play-warningarrow'),
    'required': False
  },
  'section-fail': {
    'animetable': False,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTing',
    'alter': None,
    'required': False
  },
  'section-pass': {
    'animetable': False,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTing',
    'alter': None,
    'required': False
  },
  'hit0': {
    'animetable': True,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTing',
    'alter': None,
    'required': False,
    'animationName': 'hit0-*'
  },
  'hit50': {
    'animetable': True,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTing',
    'alter': None,
    'required': False,
    'animationName': 'hit50-*'
  },
  'hit100': {
    'animetable': True,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTing',
    'alter': None,
    'required': False,
    'animationName': 'hit100-*'
  },
  'hit100k': {
    'animetable': True,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTing',
    'alter': None,
    'required': False,
    'animationName': 'hit100k-*'
  },
  'hit300': {
    'animetable': True,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTing',
    'alter': None,
    'required': False,
    'animationName': 'hit300-*'
  },
  'hit300k': {
    'animetable': True,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTing',
    'alter': None,
    'required': False,
    'animationName': 'hit300k-*'
  },
  'hit300g': {
    'animetable': True,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTing',
    'alter': None,
    'required': False,
    'animationName': 'hit300g-*'
  },
  'inputoverlay-background': {
    'animetable': False,
    'blendMode': 'normal',
    'origin': 'topRight',
    'tintType': 'noTing',
    'alter': None,
    'required': False
  },
  'inputoverlay-key': {
    'animetable': False,
    'blendMode': 'mul',
    'origin': 'center',
    'tintType': 'specific',
    'tintColor': {
      'default': (255, 255, 255),
      'pressed': {
        'topHalf': (255, 255, 0),
        'bottomHalf': (128, 0, 128)
      }
    },
    'alter': None,
    'required': False
  },
  'scorebar-bg': {
    'animetable': False,
    'blendMode': 'normal',
    'origin': 'topLeft',
    'tintType': 'noTing',
    'alter': None,
    'required': True
  },
  'scorebar-colour': {
    'animetable': True,
    'blendMode': 'normal',
    'origin': 'topLeft',
    'tintType': 'noTing',
    'alter': None,
    'required': True,
    'animationName': 'scorebar-colour-*'
  },
  'scorebar-marker': {
    'animetable': False,
    'blendMode': 'add',
    'origin': 'center',
    'tintType': 'noTing',
    'alter': None,
    'required': False
  }
}

FONT_ELEMENTS = {
  'default': {
    'animetable': False,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTint',
    'alter': None,
    'required': False,
    'urls': ('-0', '-1', '-2', '-3', '-4', '-5', '-6', '-7', '-8', '-9'),
    'prefixIdentifier': 'HitCirclePrefix',
  },
  'combo': {
    'animetable': False,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTint',
    'alter': None,
    'required': False,
    'urls': ('-0', '-1', '-2', '-3', '-4', '-5', '-6', '-7', '-8', '-9', '-x'),
    'prefixIdentifier': 'ComboPrefix',
  },
  'score': {
    'animetable': False,
    'blendMode': 'normal',
    'origin': 'center',
    'tintType': 'noTint',
    'alter': None,
    'required': False,
    'urls': ('-0', '-1', '-2', '-3', '-4', '-5', '-6', '-7', '-8', '-9', '-comma', '-dot', '-percent', '-x'),
    'prefixIdentifier': 'ScorePrefix'
  }
}
