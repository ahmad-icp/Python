# Timetable Management API

Timetable Management is exposed under `/api/v1/timetable` and depends on Academic Management sessions, classes, sections, subjects, subject allocations, and teacher assignments.

## Security

- `timetable:read` lists classrooms, slots, calendar events, versions, entries, teacher views, student/section views, and classroom views.
- `timetable:write` creates classrooms, time slots, working days, calendar events, draft versions, entries, and auto-generated schedules.
- `timetable:publish` publishes a draft version and archives previous published versions for the same section.
- `timetable:delete` is reserved for controlled deletion/archive operations.

## Core resources

- Classrooms/labs with capacity and room type.
- Time slots with start/end times and break markers.
- Working days per academic session.
- Academic calendar events and holidays.
- Versioned section timetables with effective dates.
- Timetable entries linking section, subject, teacher, classroom, weekday, and time slot.

## Validation rules

- Teachers, classrooms, and sections cannot be double-booked in the same day/time slot.
- A section cannot have duplicate lectures in the same timetable version and slot.
- Break slots cannot contain lectures.
- Room capacity must be greater than or equal to section enrollment.
- Subjects must already be allocated to the section's class.
- Teachers must already be assigned to the section/subject in Academic Management.
- Timetable entries cannot be scheduled across holidays within the timetable effective window.
- Published versions replace prior published versions for that section by archiving them.
