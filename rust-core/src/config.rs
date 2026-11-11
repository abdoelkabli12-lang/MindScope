pub const COLUMN_NAMES: [&str; 17] = [
  "Student_ID",
  "Age", 
  "Gender", 
  "Year_of_Study", 
  "Sleep_Hours", 
  "Study_Hours_Per_Week", 
  "GPA", 
  "Social_Media_Hours",
  "Screen_Time_Hours", 
  "Physical_Activity", 
  "Financial_Stress", 
  "Family_Support", 
  "Attendance_Rate", 
  "Part_Time_Job", 
  "Diet_Quality", 
  "Previous_Mental_Health_History", 
  "Mental_Health_Risk"
  ];

// pub const STUDENT_ID_COLUMN: &str = "Student_ID";
// pub const TARGET_COLUMN: &str = "Mental_Health_Risk";

pub const GENDER_CATEGORIES: [&str; 3] = ["Male", "Female", "Non-binary"];



pub const PHYSICAL_ACTIVITY_CATEGORIES: [&str; 3] = ["Low", "Moderate", "High"];



pub const DIET_QUALITY_CATEGORIES: [&str; 3] = ["Poor", "Average", "Good"];



pub const PART_TIME_JOB_CATEGORIES: [&str; 2] = ["No", "Yes"];



pub const MENTAL_HEALTH_HISTORY_CATEGORIES: [&str; 2] = ["No", "Yes"];



pub const MENTAL_HEALTH_RISK_CATEGORIE: [&str; 3] = ["Low", "Medium", "High"];

pub const YEAR_OF_STUDY: [&str; 5] = ["1", "2", "3", "4", "5"];

pub const AGE: &str = "Age";
pub const SLEEP_HOURS: &str = "Sleep_Hours";
pub const STUDY_HOURS_PER_WEEK: &str = "Study_Hours_Per_Week";
pub const GPA: &str = "GPA";
pub const SOCIAL_MEDIA_HOURS: &str = "Social_Media_Hours";
pub const SCREEN_TIME_HOURS: &str = "Screen_Time_Hours";
pub const FINANCIAL_STRESS: &str = "Financial_Stress";
pub const FAMILY_SUPPORT: &str = "Family_Support";
pub const ATTENDANCE_RATE: &str = "Attendance_Rate";

pub const NUMERICAL_COLUMNS: [&str; 9] = [
    AGE,
    SLEEP_HOURS,
    STUDY_HOURS_PER_WEEK,
    GPA,
    SOCIAL_MEDIA_HOURS,
    SCREEN_TIME_HOURS,
    FINANCIAL_STRESS,
    FAMILY_SUPPORT,
    ATTENDANCE_RATE,
];