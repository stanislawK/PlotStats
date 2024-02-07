"use server";

type Scan = {
  day: number;
  hour: number;
  minute: number;
  url: string;
};

export async function adhocScan(scan: Scan, accessToken: string) {
  const mutation = JSON.stringify({
    query: `
      mutation adhocScan {
        adhocScan(
          input: {
            url: "${scan.url}",
            schedule:	{dayOfWeek: ${scan.day}, hour: ${scan.hour}, minute: ${scan.minute}}
          }
        ) {
          ... on InputValidationError {
            __typename
            message
          }
          ... on ScanFailedError {
            __typename
            message
          }
          ... on ScanSucceeded {
            __typename
            message
          }
        }
      }`,
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
      body: mutation,
    });
    const res_parsed = await api_res.json();
    const data = res_parsed.data["adhocScan"];
    return data;
  } catch (error) {
    console.log(error);
  }
}
