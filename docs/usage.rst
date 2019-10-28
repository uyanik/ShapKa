=====
Usage
=====

To use ShapleyKano in a project::

    from shapleykano.kanomodel import KanoModel

    model = KanoModel(df, 
                  y_varname, X_varnames, 
                  analysis = 'kda',
                  y_dissat_upperbound = 6, y_sat_lowerbound = 9,
                  X_dissat_upperbound = 6, X_sat_lowerbound = 9)

    kda = model.key_drivers() ;kda
