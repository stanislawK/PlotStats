import Sidebar from "../components/sidebar";

export default function Layout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <>
        <Sidebar></Sidebar>
        {children}
        <p>but is should work Lorem ipsum dolor sit amet consectetur adipisicing elit. Nesciunt quia placeat rem neque, officiis alias sequi eaque commodi rerum natus velit expedita optio ipsum? Totam hic et cumque iure sunt.</p>
    </>
  )
}
