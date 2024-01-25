import {
  ExampleChart,
  FlowbiteChart,
  FlowbiteDemo,
} from "../components/testChart";
import Sidebar from "../components/sidebar";

export default async function Charts() {
  return (
    <>
      <div className="flex flex-col space-y-7 justify-center w-full h-full">
        <div className="mx-auto">
          <ExampleChart></ExampleChart>
        </div>
        <div className="mx-auto h-[55%]">
          <FlowbiteChart></FlowbiteChart>
        </div>
        <div>
          <FlowbiteDemo></FlowbiteDemo>
        </div>
      </div>
    </>
  );
}
