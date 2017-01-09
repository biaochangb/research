figure(1);
views=[
1198696	882483.6667	1288456	906096	860779.6667	1456326.333	911391.6667	1561576.333	847791.3333	1588571.333	840272.6667	798558	1479672.333	772246	673048	1389058.333	684371	601134.3333	1344875.333	764323	695948.3333	1349232	699562	651082	1320469.333	692643.3333	1393281.333	654864.6667	1377544.333	611998	592155.3333	1297152.667	652259	601880	1313591.333	682974.6667	666087.6667	1559821.333
];
ngram=1:1:length(views(1,:));
plot(ngram,views(1,:),'-ob','LineWidth',2);
daspect([ 8     600000           1] )
xlabel('Episode ID','fontsize',18);
ylabel('Average Popularity ','fontsize',18);
set(gca,'fontsize',16);
%printpdf(1,'teleplay_example_original.pdf');


figure(2);
views=[
0.718729083	0.597523809	1	0.95455185	0.510862926	0.27566729	0.106836977	0.255099411	0.140551997	0.519457913	0.453014371	0	0.054980386	0.337357957
];
ngram=1:1:length(views(1,:));
plot(ngram,views(1,:),'-ob','LineWidth',2);
xlabel('Update ID','fontsize',18);
ylabel('Normalized Average Popularity','fontsize',18);
set(gca,'fontsize',16);
printpdf(2,'teleplay_example_normalized.pdf');

figure(3);
views=[
0.718729083	0.597523809	1	0.95455185	0.510862926	0.27566729	0.106836977	0.255099411	0.140551997	0.519457913	0.453014371	0	0.054980386	0.337357957
];
ngram=1:1:length(views(1,:));
plot(ngram,views(1,:),'-ob','LineWidth',2);
xlabel('Update ID','fontsize',18);
ylabel('Average Popularity','fontsize',18);
set(gca,'fontsize',16);
printpdf(3,'teleplay_example_merged.pdf');


