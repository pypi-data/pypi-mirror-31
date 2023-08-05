#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* pjd.c */
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

#include "slepcpep.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pepjdsetrestart_ PEPJDSETRESTART
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pepjdsetrestart_ pepjdsetrestart
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pepjdgetrestart_ PEPJDGETRESTART
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pepjdgetrestart_ pepjdgetrestart
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pepjdsetfix_ PEPJDSETFIX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pepjdsetfix_ pepjdsetfix
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pepjdgetfix_ PEPJDGETFIX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pepjdgetfix_ pepjdgetfix
#endif


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void PETSC_STDCALL  pepjdsetrestart_(PEP pep,PetscReal *keep, int *__ierr){
*__ierr = PEPJDSetRestart(
	(PEP)PetscToPointer((pep) ),*keep);
}
PETSC_EXTERN void PETSC_STDCALL  pepjdgetrestart_(PEP pep,PetscReal *keep, int *__ierr){
*__ierr = PEPJDGetRestart(
	(PEP)PetscToPointer((pep) ),keep);
}
PETSC_EXTERN void PETSC_STDCALL  pepjdsetfix_(PEP pep,PetscReal *fix, int *__ierr){
*__ierr = PEPJDSetFix(
	(PEP)PetscToPointer((pep) ),*fix);
}
PETSC_EXTERN void PETSC_STDCALL  pepjdgetfix_(PEP pep,PetscReal *fix, int *__ierr){
*__ierr = PEPJDGetFix(
	(PEP)PetscToPointer((pep) ),fix);
}
#if defined(__cplusplus)
}
#endif
