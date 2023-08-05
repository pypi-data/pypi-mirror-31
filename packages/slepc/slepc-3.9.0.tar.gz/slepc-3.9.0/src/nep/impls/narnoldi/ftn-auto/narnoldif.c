#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* narnoldi.c */
/* Fortran interface file */

/*
* This file was generated automatically by bfort from the C source
* file.  
 */

#ifdef PETSC_USE_POINTER_CONVERSION
#if defined(__cplusplus)
extern "C" { 
#endif 
extern void *PetscToPointer(void*);
extern int PetscFromPointer(void *);
extern void PetscRmPointer(void*);
#if defined(__cplusplus)
} 
#endif 

#else

#define PetscToPointer(a) (*(PetscFortranAddr *)(a))
#define PetscFromPointer(a) (PetscFortranAddr)(a)
#define PetscRmPointer(a)
#endif

#include "slepcnep.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define nepnarnoldisetksp_ NEPNARNOLDISETKSP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define nepnarnoldisetksp_ nepnarnoldisetksp
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define nepnarnoldigetksp_ NEPNARNOLDIGETKSP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define nepnarnoldigetksp_ nepnarnoldigetksp
#endif


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void PETSC_STDCALL  nepnarnoldisetksp_(NEP nep,KSP ksp, int *__ierr){
*__ierr = NEPNArnoldiSetKSP(
	(NEP)PetscToPointer((nep) ),
	(KSP)PetscToPointer((ksp) ));
}
PETSC_EXTERN void PETSC_STDCALL  nepnarnoldigetksp_(NEP nep,KSP *ksp, int *__ierr){
*__ierr = NEPNArnoldiGetKSP(
	(NEP)PetscToPointer((nep) ),ksp);
}
#if defined(__cplusplus)
}
#endif
