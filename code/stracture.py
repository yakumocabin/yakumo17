deleteall;
##############################################
# Truncated Cone
# A tapered cylinder with a flat bottom and rop
#
# Input properties
# index: index of dielectric
# material
# r top: radius of top surface
# r bottom: radius of bottom surface
# z span: height of cone
#
# Tags: cylinder cone point truncated pillar
#
# Copyright 2010 Lumerical Solutions Inc
##############################################

# simplify variable names by removing spaces
r_top = %r top%;
r_bottom = %r bottom%;
z_span = %z span%;

r_top=r_top+1e-20;  # avoid divice by zero problem

?theta=atan((r_bottom-r_top)/z_span); # half angle of cone tip
?ht=r_top/tan(theta);     # clipped length of tip

addcustom;
set("x",0);
set("y",0);
set("z",0);

set("first axis","y");# rotate so cone is oriented along Z axis
set("rotation 1",90);
set("x span",z_span);               # remember the 90 deg rotation when trying to understand the meaning of the x/y/z span  
set("y span",2*max([r_bottom,r_top]));
set("z span",2*max([r_bottom,r_top]));
  
set("name","cone");
set("create 3D object by","revolution");

?eqn = num2str(r_top/ht)+"*(x+"+num2str((z_span/2+ht)*1e6)+")";
set("equation 1",eqn); #equation of line to be revolved

set("material",material);   # set material properies
if(get("material")=="<Object defined dielectric>") 
  { set("index",index); }