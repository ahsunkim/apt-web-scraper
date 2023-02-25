def rent_sanitizer(rent):
  return int(rent.replace('$', '').replace(',', ''))

