Este script esta pensado para que puedas pasarle los valores importantes como argumentos por linea de comandos.

En nuestro caso, estamos tomando L=250 uHy, f = 130 Khz, Bmax = 300 mT, Idc = 1.5 A, ILmax = 1.57 A, Pcu, max = 1W, esto se refleja en el comando como
```bash
python3 metodoErickson.py -l 250 -f 130 -bmax 300 -idc 1.5 -ilmax 1.57 -pmax 1
```

También existen dos archivos de especificaciones de los nucleos (nucleos.csv) y de los cables (AWG.csv), que tienen que estar a la misma altura que el script