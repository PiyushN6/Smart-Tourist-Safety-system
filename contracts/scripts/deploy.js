async function main() {
  const DigitalIDRegistry = await ethers.getContractFactory("DigitalIDRegistry");
  const contract = await DigitalIDRegistry.deploy();
  await contract.deployed();
  console.log("DigitalIDRegistry deployed to:", contract.address);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
