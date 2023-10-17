import math


def calculatedist(ulat , ulong, plat, plong):
	ulat = float(ulat)
	ulong = float(ulong)
	plat = float(plat)
	plong = float(plong)
	dlat = math.radians(plat - ulat)
	dlong = math.radians(plong - ulong)
	a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(math.radians(ulat)) * math.cos(math.radians(plat)) * math.sin(dlong / 2) * math.sin(dlong / 2)
	c =  2 * math.atan2(a**(0.5) ,(1 - a)**(0.5));
	d = 6378137 * c
	return d
