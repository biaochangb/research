#include <stdio.h>
#include <stdlib.h>
#include "main.h"


int main(int argc, char *argv[])
{
    double a[3] = {1,2,3};
    double b[3] = {2,3,4};
    double* c = addArray(a,b,3);
    for(int i=0;i<3;++i){
        printf("%f\n",c[i]);
    }

    int n =3, v =5, tid=1;
    double delta[] ={0.1,0.1,0.1};
    double gui[] = {1,2,4};
    double belta[] = {0.2,0.2,0.2,0.2,0.2};
    double hkv[] = {1,2,3,4,5};
    double gamma[] = {0.3,0.3,0.3,0.3,0.3};
    double ev[] = {2,2,2,2,3};
    double lambda[]= {0.4,0.4,0.4,0.4,0.4};
    double suv[] = {5,5,5,5,3};

    int z = getFullConditionalForX(n,v,tid,delta,gui,belta,hkv,gamma,ev,lambda,suv);
    for(int i=0;i<3;++i){
        printf("%f\n",c[i]);
    }
    printf("%d\n", z);
    printf("%d\n", MultinomialSampling(delta,3));

    system("pause");
    return 0;
}
