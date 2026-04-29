def to_camel_case(text):
  """
  credits to https://stackoverflow.com/a/60978847
  """
  s = text.replace("-", " ").replace("_", " ")
  s = s.split()
  if len(text) == 0:
    return text
  return "".join(i.capitalize() for i in s)
