# phuzzy

[![GitPitch](https://gitpitch.com/assets/badge.svg)](https://gitpitch.com/lepy/phuzzy/master?grs=github&t=beige)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/4814372e95c543a69c69004c853b17be)](https://www.codacy.com/app/lepy/phuzzy?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=lepy/phuzzy&amp;utm_campaign=Badge_Grade)
[![Coverage Status](https://coveralls.io/repos/github/lepy/phuzzy/badge.svg?branch=master)](https://coveralls.io/github/lepy/phuzzy?branch=master)
[![Travis](https://img.shields.io/travis/lepy/phuzzy.svg)](https://travis-ci.org/lepy/phuzzy)
[![Dokumentation Status](https://readthedocs.org/projects/phuzzy/badge/?version=latest)](https://phuzzy.readthedocs.io/en/latest/?badge=latest)
[![Updates](https://pyup.io/repos/github/lepy/phuzzy/shield.svg)](https://pyup.io/repos/github/lepy/phuzzy/)
[![saythanks.io/to/lepy](https://img.shields.io/badge/Say%20Thanks-!-1EAEDB.svg)](https://saythanks.io/to/lepy)

## phuzzy.Triangle

    p = phuzzy.Triangle(alpha0=[1,4], alpha1=[2], number_of_alpha_levels=5)

    p.df

       alpha   low high
    0   0.00  1.00  4.0
    1   0.25  1.25  3.5
    2   0.50  1.50  3.0
    3   0.75  1.75  2.5
    4   1.00  2.00  2.0

![](doc/triangle.png)

## phuzzy.Trapezoid

    p = phuzzy.Trapezoid(alpha0=[1,4], alpha1=[2,3], number_of_alpha_levels=5)

    p.df

       alpha   low  high
    0   0.00  1.00  4.00
    1   0.25  1.25  3.75
    2   0.50  1.50  3.50
    3   0.75  1.75  3.25
    4   1.00  2.00  3.00

![](doc/trapezoid.png)

## phuzzy.TruncNorm

    p = phuzzy.TruncNorm(alpha0=[1,3], number_of_alpha_levels=15, name="x")

    p.df

           alpha       low      high
    0   0.000000  1.000000  3.000000
    1   0.071429  1.234184  2.765816
    2   0.142857  1.342402  2.657598
    3   0.214286  1.414912  2.585088
    4   0.285714  1.472370  2.527630
    5   0.357143  1.521661  2.478339
    6   0.428571  1.566075  2.433925
    7   0.500000  1.607529  2.392471
    8   0.571429  1.647354  2.352646
    9   0.642857  1.686656  2.313344
    10  0.714286  1.726558  2.273442
    11  0.785714  1.768503  2.231497
    12  0.857143  1.814923  2.185077
    13  0.928571  1.871675  2.128325
    14  1.000000  2.000000  2.000000

![](doc/truncnorm.png)
