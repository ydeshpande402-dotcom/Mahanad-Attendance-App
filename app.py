import streamlit as st
from streamlit_geolocation import streamlit_geolocation

from auth.login import authenticate_user
from attendance.location_service import get_ground_location
from attendance.haversine import calculate_distance
from attendance.attendance_service import mark_attendance

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Mahanad Attendance",
    layout="centered"
)

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_name" not in st.session_state:
    st.session_state.user_name = ""

if "username" not in st.session_state:
    st.session_state.username = ""

if "attendance_result" not in st.session_state:
    st.session_state.attendance_result = None

# --------------------------------------------------
# LOGIN PAGE
# --------------------------------------------------

if not st.session_state.logged_in:

    col1, col2 = st.columns([1, 1])

    with col1:
        st.image("assets/logo_left.png", width=140)

    with col2:
        st.image("assets/logo_right.png", width=140)

    st.markdown(
        "<h1 style='text-align:center;'> महानाद ढोल-ताशा पथक</h1>",
        unsafe_allow_html=True
    )

    st.markdown("---")

    username = st.text_input("Username")

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button(
        "Login",
        use_container_width=True
    ):

        with st.spinner("Authenticating..."):

            is_valid, user_id, name = authenticate_user(
                username,
                password
            )

        if is_valid:

            st.session_state.logged_in = True
            st.session_state.username = user_id
            st.session_state.user_name = name

            st.rerun()

        else:

            st.error(
                "Invalid Username or Password"
            )

# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

else:

    st.success(
        f"Welcome {st.session_state.user_name}"
    )

    st.markdown("---")

    st.subheader("Attendance Portal")

    location = streamlit_geolocation()

    if location and location.get("latitude"):

        st.success(
            "📍 Location verified successfully."
        )

    else:

        st.warning(
            "Please allow GPS location access."
        )

    st.markdown("---")

    col1, col2 = st.columns(2)

    # ----------------------------------------------
    # MARK ATTENDANCE
    # ----------------------------------------------

    with col1:

        if st.button(
            "Mark Attendance",
            use_container_width=True
        ):

            if not location or not location.get("latitude"):

                st.error(
                    "Location not available. Please enable GPS."
                )

            else:

                with st.spinner(
                    "Marking attendance..."
                ):

                    ground = get_ground_location()

                    distance = calculate_distance(
                        location["latitude"],
                        location["longitude"],
                        ground["latitude"],
                        ground["longitude"]
                    )

                    result = mark_attendance(
                        username=st.session_state.username,
                        name=st.session_state.user_name,
                        latitude=location["latitude"],
                        longitude=location["longitude"],
                        distance=distance,
                        radius=ground["radius"]
                    )

                    st.session_state.attendance_result = result

                st.rerun()

    # ----------------------------------------------
    # LOGOUT
    # ----------------------------------------------

    with col2:

        if st.button(
            "Logout",
            use_container_width=True
        ):

            st.session_state.logged_in = False
            st.session_state.user_name = ""
            st.session_state.username = ""
            st.session_state.attendance_result = None

            st.rerun()

    # --------------------------------------------------
    # ATTENDANCE RESULT
    # --------------------------------------------------

    if st.session_state.attendance_result:

        result = st.session_state.attendance_result

        st.markdown("---")

        if result["success"]:

            if result["status"] == "Present":

                st.success(
                    f"Attendance Marked Successfully\n\nDistance: {result['distance']} meters"
                )

                st.image(
                    "assets/present.png",
                    use_container_width=True
                )

                st.markdown(
                    """
                    <h3 style='text-align:center; color:green;'>
                    Thank You For Being Present 🙏
                    </h3>
                    """,
                    unsafe_allow_html=True
                )

            else:

                st.error(
                    f"Outside Attendance Radius\n\nDistance: {result['distance']} meters"
                )

                st.image(
                    "assets/absent.png",
                    use_container_width=True
                )

                st.markdown(
                    """
                    <h3 style='text-align:center; color:red;'>
                    You Are Outside The Allowed Attendance Area
                    </h3>
                    """,
                    unsafe_allow_html=True
                )

        else:

            st.warning(
                result["message"]
            )