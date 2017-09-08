#ifndef __MAIN_H__
#define __MAIN_H__

#include <windows.h>

/*  To use this exported function of dll, include this header
 *  in your project.
 */

#ifdef BUILD_DLL
    #define DLL_EXPORT __declspec(dllexport)
#else
    #define DLL_EXPORT __declspec(dllimport)
#endif


#ifdef __cplusplus
extern "C"
{
#endif

int DLL_EXPORT getFullConditionalForX(int n, long v, long tid, int seed, double delta[], double gui[], double beta[], double hkv[], double gamma[], double ev[], double lambda[], double suv[]);
double DLL_EXPORT sum(double a[], int m);
double* DLL_EXPORT addArray(double a[], double b[], int m);
int DLL_EXPORT MultinomialSampling(double* p, int n, int seed, double p0);
#ifdef __cplusplus
}
#endif

#endif // __MAIN_H__
