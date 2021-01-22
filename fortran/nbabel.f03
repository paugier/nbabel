module particle_mod
   implicit none

   integer, parameter :: fint = selected_int_kind(15)
   integer, parameter :: fflt = selected_real_kind(15, 307)

   ! define particle class
   type particle
      integer(fint) :: nstars
      real(fflt) :: dt, dt2
      real(fflt), allocatable, dimension(:) :: m
      real(fflt), allocatable, dimension(:, :) :: x, v, a, aold ! position, velocity, acceleration (x2)
   contains
      procedure :: getKE
      procedure :: getAPE
      procedure :: update_x
      procedure :: update_v
      procedure :: set_aold
      procedure :: initialize
      procedure :: output
   end type

contains
   !> initialize the particle list
   subroutine initialize(P, fname)
      class(particle) :: P
      character(len=255), intent(in) :: fname
      integer(fint) :: i, dummy

      open (unit=10, file=trim(fname), status='old')
      do i = 1, P%nstars
         read (10, *) dummy, P%m(i), P%x(:, i), P%v(:, i)
      enddo !- i
      close (10)
   end subroutine initialize

   !> computes the kinetic energy
   subroutine getKE(P, KE)
      class(particle) :: P
      integer(fint) :: i
      real(fflt) :: KE

      KE = 0.0_fflt
      do i = 1, P%nstars
         KE = KE + P%m(i)*dot_product(P%v(:, i), P%v(:, i))
      enddo !- i
      KE = 0.5_fflt*KE
   end subroutine getKE

   !> computes the acceleration
   subroutine getAPE(P, PE)
      class(particle) :: P
      integer(fint) :: i, j, k
      real(fflt) :: d, d2, coeff, r(3), PE

      ! zero out accelerations & PE
      P%a(:, :) = 0.0_fflt
      PE = 0.0_fflt

      ! compute the total PE & the accelerations for each particle
      do i = 1, P%nstars - 1
         do j = i + 1, P%nstars
            r(:) = P%x(:, i) - P%x(:, j)
            d2 = dot_product(r(:), r(:))
            d = sqrt(d2)
            coeff = d*d*d
            PE = PE - P%m(i)*P%m(j)/d
            P%a(:, j) = P%a(:, j) + (P%m(i)/coeff)*r(:)
            P%a(:, i) = P%a(:, i) - (P%m(j)/coeff)*r(:)
         enddo !- j
      enddo !- i
   end subroutine getAPE

   !> update the positions, leapfrog method: X += dt*V+0.5d0*dt^2*A
   subroutine update_x(P)
      class(particle) :: P
      integer(fint) :: i

      do i = 1, P%nstars
         P%x(:, i) = P%x(:, i) + P%dt*P%v(:, i) + 0.5_fflt*P%dt2*P%a(:, i)
      enddo !- i
   end subroutine update_x

   !> update the velocities, leapfrog method: V += 0.5d0*dt*(Aold+A)
   subroutine update_v(P)
      class(particle) :: P
      integer(fint) :: i

      do i = 1, P%nstars
         P%v(:, i) = P%v(:, i) + 0.5_fflt*P%dt*(P%aold(:, i) + P%a(:, i))
      enddo !- i
   end subroutine update_v

   !> update the (old) accelerations
   subroutine set_aold(P)
      class(particle) :: P

      P%aold(:, :) = P%a(:, :)
   end subroutine set_aold

   !> output the final state
   subroutine output(P)
      class(particle) :: P
      integer(fint) :: i
      character(len=255) :: filename

      write (filename, '(a6,i0)') 'output', P%nstars

      open (unit=12, file=trim(filename), status='replace')
      do i = 1, P%nstars
         write (12, *) i, P%m(i), P%x(:, i), P%v(:, i), P%a(:, i)
      enddo !- i
      close (12)
   end subroutine output

end module particle_mod

! main program
program nbabel
   use particle_mod
   integer(fint) :: nstars, counter
   real(fflt) :: t, tend, E, KE, PE
   real(fflt) :: start_time, stop_time

   type(particle) :: pList ! particle list object
   character(len=255) :: filename, cstars, ctend
   integer :: nargs

   ! prepare file IO

   nargs = command_argument_count()

   call get_command_argument(1, filename)
   call get_command_argument(2, cstars)

   if (nargs > 2) then
      call get_command_argument(3, ctend)
      read (ctend,*) tend
   else
      tend = 10.0_fflt
   endif

   read (cstars, '(i5)') nstars
   !print *, "Enter name of input file & number of stars"
   !read *, filename, nstars

   pList%nstars = nstars
   pList%dt = 1e-3_fflt
   pList%dt2 = pList%dt**2

   ! allocate the needed memory
   allocate (pList%m(nstars), pList%x(3, nstars), &
             pList%v(3, nstars), pList%a(3, nstars), pList%aold(3, nstars))

   ! initialize
   call pList%initialize(filename)

   call cpu_time(start_time)

   t = 0.0_fflt
   counter = 0

   call pList%getAPE(PE)
   call pList%getKE(KE)
   Eold = PE + KE
   !print *, PE, KE

   do while (t < tend)
      call pList%update_x()            ! x += dt*v + 0.5*dt^2*a
      call pList%set_aold()            ! aold = a
      call pList%getAPE(PE)            ! a = F/m
      call pList%update_v()            ! v += dt*(aold + a)
      call pList%getKE(KE)                     ! KE = sum(KE_i)

      ! update time & counter
      t = t + pList%dt
      counter = counter + 1

      ! total energy
      E = PE + KE

      if (mod(counter, 100) == 0) then
         print *, "t=", t, "E=", E, "dE/E=", (E - Eold)/Eold
      endif
      Eold = E
   enddo !- while

   call pList%output()

   call cpu_time(stop_time)

   ! print out the final change
   !print *, "total dE/E = ", -(E + 0.25_fflt)/0.25_fflt
   !print *, "Elapsed time: ", stop_time - start_time
   print '(i0,2x,2(g16.8,2x))', pList%nstars, stop_time - start_time, -(E + 0.25_fflt)/0.25_fflt

end program nbabel
