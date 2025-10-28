from django.shortcuts import render, redirect
from django.contrib import messages

def home(request):
    # Clear any existing session data when returning to home
    request.session.flush()
    return render(request, 'index.html')

def select_locker(request):
    """Handle locker selection for both public and private lockers.
    For public (RFID) lockers, redirect straight to RFID authentication.
    For private lockers, proceed to PIN entry."""
    # pass a list of locker numbers to the template for iteration
    lockers = range(1, 17)
    
    # Check if this is coming from RFID (public) flow
    is_public = request.session.get('public_flow', False)
    
    if is_public:
        if request.method == 'POST':
            locker_number = request.POST.get('locker_number')
            if locker_number:
                request.session['selected_locker'] = locker_number
                # If RFID has already been authenticated (user tapped), open immediately
                if request.session.get('rfid_authenticated'):
                    return redirect('open_locker')
                return redirect('rfid_login')
    
    return render(request, 'selectLocker.html', {'lockers': lockers, 'is_public': is_public})

def rfid_login(request):
    """Handle RFID authentication for public lockers."""
    # Allow the RFID page to be shown first. A POST simulates the tap.
    request.session['public_flow'] = True

    if request.method == 'POST':
        # mark that the user has tapped their RFID card
        request.session['rfid_authenticated'] = True
        # if a locker is already selected, open it immediately
        if request.session.get('selected_locker'):
            return redirect('open_locker')
        # otherwise go to locker selection
        return redirect('select_locker')

    # GET: render the RFID prompt (may include selected_locker if already set)
    selected_locker = request.session.get('selected_locker')
    return render(request, 'rfid.html', {
        'selected_locker': selected_locker
    })

def open_locker(request):
    """Simulate opening the selected locker for public flow.

    Clears RFID-related session flags after opening so the flow must be
    restarted for another action.
    """
    locker = request.session.get('selected_locker')
    # clear flow flags to avoid reuse
    request.session.pop('rfid_authenticated', None)
    request.session.pop('selected_locker', None)
    request.session.pop('public_flow', None)

    return render(request, 'open_locker.html', {'locker': locker})

def private_auth(request):
    """Redirect private access requests to locker selection.

    The `private_auth.html` template has been removed. Redirect users to
    the locker selection page so they can choose a locker and proceed with
    the private flow (PIN → fingerprint).
    """
    return redirect('select_locker')

def pin_entry(request):
    """Show PIN entry form (GET) and validate PIN on POST.

    For now this uses a hard-coded demo PIN. On successful entry the
    user is redirected to the fingerprint flow (as requested).
    """
    # respect an optional `next` parameter (GET or POST) to control where to go
    next_target = request.GET.get('next') or request.POST.get('next')

    if request.method == 'POST':
        # Store the locker number in the session if it's provided
        locker_number = request.POST.get('locker_number')
        if locker_number:
            request.session['selected_locker'] = locker_number
            return render(request, 'pin.html', {'selected_locker': locker_number})

        pin = request.POST.get('pin', '').strip()
        # demo PIN — change or replace with real auth lookup as needed
        DEMO_PIN = '1234'
        if pin == DEMO_PIN:
            # PIN correct — mark session
            request.session['pin_verified'] = True
            # If a next target was provided, honor it (only allow 'fingerprint' for now)
            if next_target == 'fingerprint':
                return redirect('fingerprint_login')
            return redirect('fingerprint_login')
        else:
            messages.error(request, 'Incorrect PIN. Please try again.')

    return render(request, 'pin.html')

def fingerprint_login(request):
    """Require a successful PIN verification before showing fingerprint page.

    If the user reaches this view without a successful PIN, redirect them to
    the PIN entry page (and request fingerprint as the `next` target).
    After rendering the fingerprint page, clear the `pin_verified` flag so the
    user must re-enter the PIN next time.
    """
    if not request.session.get('pin_verified'):
        # request PIN, and ask to continue to fingerprint after success
        return redirect(f"{request.path.replace('fingerprint/', 'pin/')}?next=fingerprint")

    # clear flag so fingerprint cannot be accessed again without PIN
    try:
        del request.session['pin_verified']
    except KeyError:
        pass

    return render(request, 'fingerprint.html')
