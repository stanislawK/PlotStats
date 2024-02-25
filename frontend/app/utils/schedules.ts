"use server";

type RawUserSchedules = {
  category: {
    name: string;
  };
  distanceRadius: number;
  id: number;
  location: string;
  schedule?: {
    dayOfWeek: number;
    hour: number;
    minute: number;
  };
}[];

const DaysMap = {
  1: "Monday",
  2: "Tuesday",
  3: "Wednesday",
  4: "Thursday",
  5: "Friday",
  6: "Saturday",
  0: "Sunday",
};

export async function findSearchById(
  userSchedules: RawUserSchedules,
  searchId: number
) {
  let search;
  try {
    search = userSchedules.find((schedule) => schedule.id == searchId);
  } catch (error) {
    console.log(error);
  }
  return search;
}

export async function parseSchedules(userSchedules: RawUserSchedules) {
  let sortedSchedules = {
    Monday: {},
    Tuesday: {},
    Wednesday: {},
    Thursday: {},
    Friday: {},
    Saturday: {},
    Sunday: {},
    disabled: [],
  };
  userSchedules.map((schedule) => {
    if (!!schedule?.schedule) {
      const { dayOfWeek, hour, minute } = schedule.schedule;
      const day = DaysMap[dayOfWeek];
      const formattedHour = hour.toString().padStart(2, "0");
      const formattedMinute = minute.toString().padStart(2, "0");
      const key = `${formattedHour}:${formattedMinute}`;
      if (key in sortedSchedules[day]) {
        sortedSchedules[day][key].push(schedule);
      } else {
        sortedSchedules[day][key] = [schedule];
      }
    } else {
      sortedSchedules.disabled.push(schedule);
    }
  });
  return sortedSchedules;
}

export async function getUserSchedules(accessToken: string) {
  const query = JSON.stringify({
    query: `
      query usersSearches {
        usersSearches {
          ... on SearchesType {
            __typename
            searches {
              category {
                name
              }
              distanceRadius
              id
              location
              schedule {
                dayOfWeek
                hour
                minute
              }
            }
          }
          ... on NoSearchesAvailableError {
            __typename
            message
          }
        }
      }
      `,
  });
  try {
    const api_res = await fetch("http://backend:8000/graphql", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        Authorization: `Bearer ${accessToken}`,
      },
      body: query,
    });
    const res_parsed = await api_res.json();
    const data = res_parsed.data["usersSearches"]["searches"];
    return data;
  } catch (error) {
    console.log(error);
  }
}

export async function editSchedule(
  accessToken: string,
  id: number,
  day: number,
  hour: number,
  minute: number
) {
  const query = JSON.stringify({
    query: `
      mutation editSchedule {
        editSchedule(input: {id: ${id}, schedule: {dayOfWeek: ${day}, hour: ${hour}, minute: ${minute}}}) {
          ... on ScheduleEditedSuccessfully {
            __typename
            message
          }
          ... on SearchDoesntExistError {
            __typename
            message
          }
          ... on InputValidationError {
            __typename
            message
          }
        }
      }
      `,
  });
  try {
    const api_res = await fetch("http://backend:8000/graphql", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        Authorization: `Bearer ${accessToken}`,
      },
      body: query,
    });
    const res_parsed = await api_res.json();
    const data = res_parsed.data["editSchedule"]["ScheduleEditedSuccessfully"];
    return data;
  } catch (error) {
    console.log(error);
  }
}

export async function disableSchedule(accessToken: string, id: number) {
  const query = JSON.stringify({
    query: `
      mutation editSchedule {
        editSchedule(input: {id: ${id}}) {
          ... on ScheduleEditedSuccessfully {
            __typename
            message
          }
          ... on SearchDoesntExistError {
            __typename
            message
          }
          ... on InputValidationError {
            __typename
            message
          }
        }
      }
      `,
  });
  try {
    const api_res = await fetch("http://backend:8000/graphql", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        Authorization: `Bearer ${accessToken}`,
      },
      body: query,
    });
    const res_parsed = await api_res.json();
    const data = res_parsed.data["editSchedule"]["ScheduleEditedSuccessfully"];
    return data;
  } catch (error) {
    console.log(error);
  }
}
