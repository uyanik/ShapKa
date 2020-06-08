=====
Usage
=====

To use ShapKa in a project::

    from ShapKa.kanomodel import KanoModel

    model = KanoModel(df, 
                  y_varname, X_varnames, 
                  analysis = 'kda',
                  y_dissat_upperbound = 6, y_sat_lowerbound = 9,
                  X_dissat_upperbound = 6, X_sat_lowerbound = 9,
                  weight_varname)

    kda = model.key_drivers() ;kda
