# Mesure electrical consumption with GRID5000

```bash
ssh g5k
ssh lyon
oarsub -p "cluster='taurus'" -l nodes=1,walltime=4:00 -I
oarsub -p "host='taurus-12.lyon.grid5000.fr'" -l nodes=1,walltime=4:00 -I
```

Benchmarks run in Taurus node at Grid 5000:

2.30 GHz Intel Xeon E5-2630, node with 2 CPUs, 6 cores/CPU, 32GB RAM, 557GB HDD, 1 x 10Gb Ethernet

Compared to Zwart (2020):

2.7 GHz Intel Xeon E-2176M