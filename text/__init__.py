""" from https://github.com/keithito/tacotron """
from text import cleaners
# from text.symbols import symbols

# _symbol_to_id = {s: i for i, s in enumerate(symbols)}
def text_to_sequence(text, symbols, cleaner_names):
  '''Converts a string of text to a sequence of IDs corresponding to the symbols in the text.
    Args:
      text: string to convert to a sequence
      cleaner_names: names of the cleaner functions to run the text through
    Returns:
      List of integers corresponding to the symbols in the text
  '''
  _symbol_to_id = {s: i for i, s in enumerate(symbols)}

  sequence = []

  clean_text = _clean_text(text, cleaner_names)

  sequence = [
        _symbol_to_id[symbol] for symbol in clean_text if symbol in _symbol_to_id.keys()
    ]
  return sequence

def text_to_sequence2(text,symbols, cleaner_names):
  '''Converts a string of text to a sequence of IDs corresponding to the symbols in the text.
    Args:
      text: string to convert to a sequence
      cleaner_names: names of the cleaner functions to run the text through
    Returns:
      List of integers corresponding to the symbols in the text
  '''
  sequence = []
  _symbol_to_id = {s: i for i, s in enumerate(symbols)}

  clean_text = _clean_text(text, cleaner_names)

  for symbol in clean_text.split(" "):
    if symbol in _symbol_to_id:
      sequence.append(_symbol_to_id[symbol])
    else:
      for s in symbol:
        sequence.append(_symbol_to_id[s])
    sequence.append(_symbol_to_id[" "])
  if sequence[-1] == _symbol_to_id[" "]:
    sequence = sequence[:-1]
  return sequence

def _clean_text(text, cleaner_names, if_show=True):
  for name in cleaner_names:
    cleaner = getattr(cleaners, name)
    if not cleaner:
      raise Exception('Unknown cleaner: %s' % name)
    text = cleaner(text)
    if if_show:
      print(text)
  return text
