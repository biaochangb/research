#include "main.h"
#include <time.h>
#include <stdlib.h>
#include <stdio.h>

int DLL_EXPORT MultinomialSampling(double* p, int n, int seed, double p0){
    double ps = sum(p,n);
    //double * cumulative_sum_p = (double *)malloc(n* sizeof(double));
    int i=0;
    //srand(seed);
    //double r = rand()*1.0/RAND_MAX;
    for(i=0;i<n;i++){
        p[i] = p[i]/ps;
        if(i>0){
            p[i] += p[i-1]; //cumulative_sum of p
        }
        if(p0<p[i]){
            break;
        }
    }
    /*
    for(i=0;i<n;i++){
        cumulative_sum_p[i] = p[i]/ps;
        if(i>0){
            cumulative_sum_p[i] += cumulative_sum_p[i-1];
        }
    }
    srand(seed);
    double r = rand()*1.0/RAND_MAX;
    for(i=0;i<n;i++){
        if(r<cumulative_sum_p[i]){
            break;
        }
    }
    free(cumulative_sum_p);*/
    return i;
}

// a sample exported function
int DLL_EXPORT getFullConditionalForX(int n, long v, long tid, int seed, double delta[], double gui[], double beta[], double hkv[], double gamma[], double ev[], double lambda[], double suv[])
{
    double* p = (double *)malloc(n* sizeof(double));
    double* delta_gui, *beta_hkv, *gamma_ev, *lambda_suv;
    double sum_delta_gui, sum_beta_hkv, sum_gamma_ev, sum_lambda_suv;
    delta_gui = addArray(delta,gui,n);
    beta_hkv = addArray(beta,hkv,v);
    gamma_ev = addArray(gamma,ev,v);
    lambda_suv = addArray(lambda,suv,v);

    //sum_delta_gui = sum(delta_gui,n);
    sum_beta_hkv = sum(beta_hkv,v);
    sum_gamma_ev = sum(gamma_ev,v);
    sum_lambda_suv = sum(lambda_suv,v);

    p[0] = delta_gui[0]*beta_hkv[tid]/sum_beta_hkv;
    p[1] = delta_gui[1]*gamma_ev[tid]/sum_gamma_ev;
    p[2] = delta_gui[2]*lambda_suv[tid]/sum_lambda_suv;

    //printf("%lf,%lf,%lf\n",p[0],p[1],p[2]);
    int x = MultinomialSampling(p, n, seed, 0.1);

    free(delta_gui);
    free(beta_hkv);
    free(gamma_ev);
    free(lambda_suv);
    free(p);

    return x;
}

double DLL_EXPORT sum(double a[], int m){
    double s = 0;
    int i=0;
    for(i=0;i<m;i++){
        s += a[i];
    }
    return s;
}

double* DLL_EXPORT addArray(double a[], double b[], int m){
    double *s = (double *)malloc(m * sizeof(double));
    int i=0;
    for(i=0;i<m;i++){
        s[i] = a[i]+b[i];
    }
    return s;
}
