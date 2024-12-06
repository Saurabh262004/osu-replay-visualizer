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
  'names': ('general', 'editor', 'metadata', 'difficulty', 'events', 'timingPoints', 'colours', 'hitobjects'),
  'headers': ('[General]\n', '[Editor]\n', '[Metadata]\n', '[Difficulty]\n', '[Events]\n', '[TimingPoints]\n', '[Colours]\n', '[HitObjects]\n'),
  'types': ('kvp', 'kvp', 'kvp', 'kvp', 'csl', 'csl', 'kvp', 'csl')
}
