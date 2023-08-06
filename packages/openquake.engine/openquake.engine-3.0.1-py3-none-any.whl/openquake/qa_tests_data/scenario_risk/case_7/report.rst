Scenario Risk Test
==================

============== ===================
checksum32     4,057,024,737      
date           2018-03-26T15:57:44
engine_version 2.10.0-git543cfb0  
============== ===================

num_sites = 27, num_levels = 8

Parameters
----------
=============================== ===============
calculation_mode                'scenario_risk'
number_of_logic_tree_samples    0              
maximum_distance                None           
investigation_time              None           
ses_per_logic_tree_path         1              
truncation_level                None           
rupture_mesh_spacing            None           
complex_fault_mesh_spacing      None           
width_of_mfd_bin                None           
area_source_discretization      None           
ground_motion_correlation_model None           
minimum_intensity               {}             
random_seed                     42             
master_seed                     0              
ses_seed                        42             
avg_losses                      True           
=============================== ===============

Input files
-----------
======================== ================================================================
Name                     File                                                            
======================== ================================================================
exposure                 `exposurePathSines.xml <exposurePathSines.xml>`_                
gmfs                     `gmfs.csv <gmfs.csv>`_                                          
job_ini                  `job.ini <job.ini>`_                                            
structural_vulnerability `vulnerability_model_test1.xml <vulnerability_model_test1.xml>`_
======================== ================================================================

Composite source model
----------------------
========= ====== =============== ================
smlt_path weight gsim_logic_tree num_realizations
========= ====== =============== ================
b_1       1.000  trivial(1)      1/1             
========= ====== =============== ================

Realizations per (TRT, GSIM)
----------------------------

::

  <RlzsAssoc(size=1, rlzs=1)
  0,FromFile: [0]>

Exposure model
--------------
=============== ========
#assets         27      
#taxonomies     4       
deductibile     absolute
insurance_limit absolute
=============== ========

======== ===== ====== === === ========= ==========
taxonomy mean  stddev min max num_sites num_assets
2        1.000 0.0    1   1   4         4         
4        1.000 0.0    1   1   16        16        
3        1.000 0.0    1   1   5         5         
1        1.000 0.0    1   1   2         2         
*ALL*    1.000 0.0    1   1   27        27        
======== ===== ====== === === ========= ==========

Slowest operations
------------------
======================= ========= ========= ======
operation               time_sec  memory_mb counts
======================= ========= ========= ======
building riskinputs     0.078     0.0       1     
reading exposure        0.010     0.0       1     
building epsilons       6.540E-04 0.0       1     
reading site collection 6.604E-05 0.0       1     
======================= ========= ========= ======